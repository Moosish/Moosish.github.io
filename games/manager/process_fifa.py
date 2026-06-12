#!/usr/bin/env python3
"""
process_fifa.py  —  FIFA / EA FC dataset → games/manager/players.js

Downloads (or reads) player data for FIFA 15 through EA FC 26 and outputs
a compact players.js file used by the Football Manager game.

Usage
-----
  # Auto-download everything via Kaggle API (requires ~/.kaggle/kaggle.json):
  python process_fifa.py --download

  # Point at CSV(s) you already downloaded:
  python process_fifa.py --csv players_24.csv fc25_male_players.csv fc26_players.csv

Datasets downloaded (in order, all merged):
  joebeachcapital/fifa-players              FIFA 15-24 combined (has fifa_version col)
  nyagami/ea-sports-fc-25-database-ratings-and-stats   EA FC 25 (2024/25)
  rovnez/fc-26-fifa-26-player-data          EA FC 26 (2025/26)  ← latest

Column structure (sofifa-format, all datasets):
  sofifa_id, short_name, player_positions, overall, dob,
  nationality_name, club_name, league_name, league_level,
  pace, shooting, passing, dribbling, defending, physic
  [+ fifa_version in multi-year set; year inferred from filename otherwise]
"""

import csv, json, sys, re, subprocess, argparse
from pathlib import Path
from collections import Counter, defaultdict

OUT_FILE = Path(__file__).resolve().parent / "players.js"
DATA_DIR = Path(__file__).resolve().parent / "fifa_data"

# ── League filter (FIFA name → game id) ─────────────────────────────────────
LEAGUE_MAP = {
    "English Premier League":     "epl",
    "Spain Primera División":     "laliga",
    "German 1. Bundesliga":       "bundesliga",
    "Italian Serie A":            "seriea",
    "French Ligue 1":             "ligue1",
    # alternate spellings found in some versions
    "Premier League":             "epl",
    "LaLiga":                     "laliga",
    "La Liga":                    "laliga",
    "LALIGA EA SPORTS":           "laliga",
    "Bundesliga":                 "bundesliga",
    "Serie A":                    "seriea",
    "Serie A Enilive":            "seriea",
    "Ligue 1":                    "ligue1",
    "Ligue 1 Uber Eats":          "ligue1",
    "Ligue 1 McDonald's":         "ligue1",
    "Ligue 1 McDonald’s":    "ligue1",  # curly apostrophe variant
}

# ── Club name → game id ──────────────────────────────────────────────────────
CLUB_MAP = {
    # EPL
    "Manchester City":"mci","Arsenal":"ars","Liverpool":"liv",
    "Chelsea":"che","Manchester United":"mun","Manchester Utd":"mun",
    "Tottenham Hotspur":"tot","Tottenham":"tot",
    "Newcastle United":"new","Aston Villa":"avl",
    "West Ham United":"whu","West Ham":"whu",
    "Brighton & Hove Albion":"bha","Brighton":"bha",
    "Brentford":"bre",
    "Wolverhampton Wanderers":"wol","Wolves":"wol",
    "Crystal Palace":"cry","Everton":"eve","Leicester City":"lei",
    "Nottingham Forest":"nfo","Nottm Forest":"nfo",
    "AFC Bournemouth":"bou","Bournemouth":"bou",
    "Fulham":"ful","Southampton":"sou","Ipswich Town":"ips","Ipswich":"ips",
    # La Liga
    "Real Madrid CF":"rma","Real Madrid":"rma",
    "FC Barcelona":"bar","Barcelona":"bar",
    "Atlético de Madrid":"atm","Atlético Madrid":"atm","Atletico Madrid":"atm",
    "Sevilla FC":"sev","Sevilla":"sev",
    "Athletic Club":"bil","Athletic Club de Bilbao":"bil","Athletic Bilbao":"bil",
    "Real Sociedad":"rso","Real Sociedad de Fútbol":"rso",
    "Villarreal CF":"vil","Villarreal":"vil",
    "Real Betis":"bet","Real Betis Balompié":"bet",
    "Valencia CF":"val","Valencia":"val",
    "Girona FC":"gir","Girona":"gir",
    "Getafe CF":"get","Getafe":"get",
    "RCD Mallorca":"mal","Mallorca":"mal",
    "CA Osasuna":"osa","Osasuna":"osa",
    "RC Celta":"cel","Celta de Vigo":"cel","Celta Vigo":"cel",
    "Rayo Vallecano":"ray","Rayo Vallecano de Madrid":"ray",
    "Deportivo Alavés":"ala","Alavés":"ala",
    "RCD Espanyol":"esp","Espanyol":"esp",
    "UD Las Palmas":"las","Las Palmas":"las",
    "CD Leganés":"leg","Leganés":"leg",
    "Real Valladolid CF":"vld","Real Valladolid":"vld","Valladolid":"vld",
    # Bundesliga
    "FC Bayern München":"bay","Bayern Munich":"bay","FC Bayern Munich":"bay",
    "Borussia Dortmund":"bvb","Dortmund":"bvb",
    "Bayer 04 Leverkusen":"lev","Bayer Leverkusen":"lev",
    "RB Leipzig":"rbl",
    "Eintracht Frankfurt":"sge",
    "VfB Stuttgart":"vfb","Stuttgart":"vfb",
    "Werder Bremen":"wer","SV Werder Bremen":"wer",
    "Borussia Mönchengladbach":"bmg","Mönchengladbach":"bmg","Borussia M'gladbach":"bmg",
    "1. FC Union Berlin":"fcu","Union Berlin":"fcu",
    "SC Freiburg":"scf","Freiburg":"scf",
    "TSG 1899 Hoffenheim":"tsg","Hoffenheim":"tsg","TSG Hoffenheim":"tsg",
    "1. FSV Mainz 05":"m05","Mainz 05":"m05","Mainz":"m05","FSV Mainz 05":"m05",
    "FC Augsburg":"aug","Augsburg":"aug",
    "FC St. Pauli":"stp","St. Pauli":"stp",
    "1. FC Köln":"koe","FC Köln":"koe","Köln":"koe",
    "Holstein Kiel":"kie",
    "VfL Wolfsburg":"wob","Wolfsburg":"wob",
    "VfL Bochum 1848":"boc","Bochum":"boc","VfL Bochum":"boc",
    # Serie A
    "Juventus":"juve","Juventus FC":"juve",
    "Inter":"int","FC Internazionale Milano":"int","Internazionale":"int",
    "AC Milan":"mil","Milan":"mil",
    "SSC Napoli":"nap","Napoli":"nap",
    "AS Roma":"rom","Roma":"rom",
    "SS Lazio":"laz","Lazio":"laz",
    "Atalanta BC":"ata","Atalanta":"ata",
    "ACF Fiorentina":"fio","Fiorentina":"fio",
    "Bologna FC 1909":"bol","Bologna":"bol",
    "Torino FC":"tor","Torino":"tor",
    "Genoa CFC":"gen","Genoa":"gen",
    "Udinese Calcio":"udi","Udinese":"udi",
    "Cagliari Calcio":"cag","Cagliari":"cag",
    "US Sassuolo Calcio":"sas","Sassuolo":"sas",
    "Hellas Verona":"ver","Verona":"ver",
    "Empoli FC":"emp","Empoli":"emp",
    "Parma Calcio 1913":"par","Parma":"par",
    "Como 1907":"com","Como":"com",
    "AC Monza":"mon","Monza":"mon",
    "Venezia FC":"ven","Venezia":"ven",
    "Sampdoria":"sam","UC Sampdoria":"sam",
    # Ligue 1
    "Paris Saint-Germain":"psg","PSG":"psg","Paris SG":"psg",
    "Olympique Lyonnais":"oly","Lyon":"oly","Olympique Lyon":"oly",
    "Olympique de Marseille":"mar","Marseille":"mar",
    "AS Monaco":"asm","Monaco":"asm",
    "OGC Nice":"nic","Nice":"nic",
    "RC Lens":"len","Lens":"len",
    "LOSC Lille":"lil","Lille":"lil","LOSC":"lil",
    "Stade Rennais FC":"ren","Rennes":"ren","Stade Rennais":"ren",
    "FC Girondins de Bordeaux":"bor","Bordeaux":"bor","Girondins de Bordeaux":"bor",
    "RC Strasbourg Alsace":"str","Strasbourg":"str","RC Strasbourg":"str",
    "Montpellier HSC":"mtp","Montpellier":"mtp",
    "FC Nantes":"nan","Nantes":"nan",
    "Toulouse FC":"tou","Toulouse":"tou",
    "Stade de Reims":"rei","Reims":"rei",
    "Stade Brestois 29":"brest","Brest":"brest",
    "Le Havre AC":"hav","Le Havre":"hav",
    "Clermont Foot":"clf","Clermont":"clf","Clermont Foot 63":"clf",
    "FC Metz":"metz","Metz":"metz",
    "Angers SCO":"ang","Angers":"ang",
    "Troyes AC":"troy","Troyes":"troy",
    "Lorient":"lor","FC Lorient":"lor",
    "Ajaccio":"aja","AC Ajaccio":"aja",
    "Auxerre":"aux","AJ Auxerre":"aux",
}

# Reverse map: club id → league id (for FC24 which has no League column)
CLUB_TO_LEAGUE = {
    "mci":"epl","ars":"epl","liv":"epl","che":"epl","mun":"epl",
    "tot":"epl","new":"epl","avl":"epl","whu":"epl","bha":"epl",
    "bre":"epl","wol":"epl","cry":"epl","eve":"epl","lei":"epl",
    "nfo":"epl","bou":"epl","ful":"epl","sou":"epl","ips":"epl",
    "rma":"laliga","bar":"laliga","atm":"laliga","sev":"laliga",
    "bil":"laliga","rso":"laliga","vil":"laliga","bet":"laliga",
    "val":"laliga","gir":"laliga","get":"laliga","mal":"laliga",
    "osa":"laliga","cel":"laliga","ray":"laliga","ala":"laliga",
    "esp":"laliga","las":"laliga","leg":"laliga","vld":"laliga",
    "bay":"bundesliga","bvb":"bundesliga","lev":"bundesliga",
    "rbl":"bundesliga","sge":"bundesliga","vfb":"bundesliga",
    "wer":"bundesliga","bmg":"bundesliga","fcu":"bundesliga",
    "scf":"bundesliga","tsg":"bundesliga","m05":"bundesliga",
    "aug":"bundesliga","stp":"bundesliga","koe":"bundesliga",
    "kie":"bundesliga","wob":"bundesliga","boc":"bundesliga",
    "juve":"seriea","int":"seriea","mil":"seriea","nap":"seriea",
    "rom":"seriea","laz":"seriea","ata":"seriea","fio":"seriea",
    "bol":"seriea","tor":"seriea","gen":"seriea","udi":"seriea",
    "cag":"seriea","sas":"seriea","ver":"seriea","emp":"seriea",
    "par":"seriea","com":"seriea","mon":"seriea","ven":"seriea","sam":"seriea",
    "psg":"ligue1","oly":"ligue1","mar":"ligue1","asm":"ligue1",
    "nic":"ligue1","len":"ligue1","lil":"ligue1","ren":"ligue1",
    "bor":"ligue1","str":"ligue1","mtp":"ligue1","nan":"ligue1",
    "tou":"ligue1","rei":"ligue1","brest":"ligue1","hav":"ligue1",
    "clf":"ligue1","metz":"ligue1","ang":"ligue1","troy":"ligue1",
    "lor":"ligue1","aja":"ligue1","aux":"ligue1",
}

# Position normalisation
POS_MAP = {
    "GK":"GK",
    "CB":"CB","RCB":"CB","LCB":"CB",
    "RB":"RB","LB":"LB",
    "RWB":"RWB","LWB":"LWB",
    "CDM":"CDM","RDM":"CDM","LDM":"CDM",
    "CM":"CM","RCM":"CM","LCM":"CM",
    "CAM":"CAM","RAM":"CAM","LAM":"CAM",
    "RM":"RM","LM":"LM",
    "RW":"RW","LW":"LW",
    "CF":"CF","RF":"CF","LF":"CF","SS":"CF",
    "ST":"ST","RS":"ST","LS":"ST",
}

def primary_pos(s):
    for tok in str(s).split(","):
        p = tok.strip()
        if p in POS_MAP:
            return POS_MAP[p]
    return None

def born_year(dob):
    m = re.match(r"(\d{4})", str(dob))
    return int(m.group(1)) if m else None

def version_from_filename(stem):
    """
    Extract FIFA version from a filename stem or directory name.
    Examples: players_25 → 25, fc25_male → 25, 2024 → 24, fc26 → 26
    Returns int version or None.
    """
    s = stem.lower()
    # 4-digit year like directory name "2024" → version 24
    m = re.fullmatch(r'20(\d{2})', s)
    if m:
        v = int(m.group(1))
        if 15 <= v <= 30:
            return v
    # Look for 2-digit number after 'fc', 'players_', or standalone
    patterns = [
        r'fc[_\s]?(\d{2})\b',           # fc25, fc_25, fc 25
        r'players[_\s](\d{2})\b',        # players_25, players_26
        r'\bfc(\d{2})[^0-9]',            # fc25_male
        r'[_\-\s](\d{2})[_\-\s]',        # _25_, -25-
        r'(\d{2})$',                      # ends with 25 or 26
    ]
    for pat in patterns:
        m = re.search(pat, s)
        if m:
            v = int(m.group(1))
            if 15 <= v <= 30:             # sane FIFA version range
                return v
    return None

def game_year_from_row(row, fields, filename_version=None):
    """
    Map FIFA version to the season start year.
    FIFA/FC 22 released Sept 2021 → 2021/22 season → game year 2021.
    Formula: game_year = 2000 + version - 1
      FC 25 → 2024, FC 26 → 2025, FIFA 22 → 2021, FIFA 15 → 2014
    """
    # 1. Explicit column in multi-year datasets
    if "fifa_version" in fields:
        try:
            v = int(float(row["fifa_version"]))
            if 15 <= v <= 30:
                return 2000 + v - 1
        except (ValueError, TypeError):
            pass
    # 2. Inferred from filename (single-year datasets)
    if filename_version is not None:
        return 2000 + filename_version - 1
    # 3. fifa_update date (some stefanoleone datasets)
    if "fifa_update" in fields:
        m = re.match(r"(\d{4})", str(row.get("fifa_update", "")))
        if m:
            return int(m.group(1)) - 1
    return 2023  # safe fallback

def si(val, default=0):
    try:
        v = int(float(val))
        return v if v > 0 else default
    except (ValueError, TypeError):
        return default

def process_csv(path, db):
    path = Path(path)
    if not path.exists():
        print(f"  SKIP {path} (not found)")
        return 0
    # Detect version from filename, then parent directory name
    file_ver = version_from_filename(path.stem)
    if file_ver is None:
        file_ver = version_from_filename(path.parent.name)

    count = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])

        # Detect EA FC format by presence of "Name" column (not sofifa-style "short_name")
        is_eafc_noleague = "Club" in fields and "Name" in fields and "league_name" not in fields and "League" not in fields
        is_eafc_league   = "Team" in fields and "League" in fields and "Name" in fields and "league_name" not in fields

        for row in reader:
            # Skip female players in combined files
            gender = row.get("Gender") or row.get("gender") or ""
            if gender.upper() == "F":
                continue

            if is_eafc_noleague:
                # FC24 format: Name, Nation, Club, Position, Age, Overall, Pace, Shooting…
                club_id = CLUB_MAP.get(row.get("Club", "").strip())
                if not club_id:
                    continue
                league_id = CLUB_TO_LEAGUE.get(club_id)
                if not league_id:
                    continue
                pos = primary_pos(row.get("Position", ""))
                if not pos:
                    continue
                age = si(row.get("Age", 0))
                if age < 14 or age > 45:
                    continue
                yr  = game_year_from_row(row, fields, file_ver)
                b   = yr - age
                name = row.get("Name", "").strip()
                if not name:
                    continue
                nat  = row.get("Nation", "")[:3].upper()
                ovr  = si(row.get("Overall", 0))
                pac  = si(row.get("Pace", 0))
                sho  = si(row.get("Shooting", 0))
                pas  = si(row.get("Passing", 0))
                dri  = si(row.get("Dribbling", 0))
                defd = si(row.get("Defending", 0))
                phy  = si(row.get("Physicality", 0))
                key  = f"{name}|{b}"

            elif is_eafc_league:
                # FC25 format: Name, OVR, PAC, SHO…, Age, Nation, League, Team
                league_id = LEAGUE_MAP.get(row.get("League", "").strip())
                if not league_id:
                    continue
                club_id = CLUB_MAP.get(row.get("Team", "").strip())
                if not club_id:
                    continue
                pos = primary_pos(row.get("Position", ""))
                if not pos:
                    continue
                age = si(row.get("Age", 0))
                if age < 14 or age > 45:
                    continue
                yr  = game_year_from_row(row, fields, file_ver)
                b   = yr - age
                name = row.get("Name", "").strip()
                if not name:
                    continue
                nat  = row.get("Nation", "")[:3].upper()
                ovr  = si(row.get("OVR", 0))
                pac  = si(row.get("PAC", 0))
                sho  = si(row.get("SHO", 0))
                pas  = si(row.get("PAS", 0))
                dri  = si(row.get("DRI", 0))
                defd = si(row.get("DEF", 0))
                phy  = si(row.get("PHY", 0))
                key  = f"{name}|{b}"

            else:
                # Standard sofifa format (FIFA 15-23, FC26)
                league_id = LEAGUE_MAP.get(row.get("league_name", ""))
                if not league_id:
                    continue
                if si(row.get("league_level", 1)) != 1:
                    continue
                club_id = CLUB_MAP.get(row.get("club_name", ""))
                if not club_id:
                    continue
                pos = primary_pos(row.get("player_positions", row.get("club_position", "")))
                if not pos:
                    continue
                b = born_year(row.get("dob", row.get("birth_date", "")))
                if not b:
                    continue
                name  = row.get("short_name", row.get("long_name", "")).strip()
                nat   = row.get("nationality_name", "")[:3].upper()
                ovr   = si(row.get("overall", 0))
                pac   = si(row.get("pace", row.get("movement_sprint_speed", 0)))
                sho   = si(row.get("shooting", 0))
                pas   = si(row.get("passing", 0))
                dri   = si(row.get("dribbling", 0))
                defd  = si(row.get("defending", 0))
                phy   = si(row.get("physic", row.get("physical", 0)))
                # GKs have blank outfield aggregate stats — use GK-specific columns instead
                if pos == 'GK' and pac + sho + pas + dri + defd + phy == 0:
                    sho  = si(row.get("goalkeeping_diving", 0))
                    pas  = si(row.get("goalkeeping_handling", 0))
                    dri  = si(row.get("goalkeeping_reflexes", 0))
                    defd = si(row.get("goalkeeping_positioning", 0))
                    pac  = si(row.get("goalkeeping_kicking", 0))
                    phy  = si(row.get("goalkeeping_speed", row.get("movement_sprint_speed", 0)))
                yr    = game_year_from_row(row, fields, file_ver)
                key   = row.get("sofifa_id") or row.get("player_id") or f"{name}|{b}"

            if pac + sho + pas + dri + defd + phy == 0:
                continue

            # Key: one entry per (player, year) — multiple years per player are kept
            year_key = f"{key}|{yr}"
            db[year_key] = dict(
                name=name, pos=pos, born=b, yr=yr,
                club=club_id, league=league_id, nat=nat,
                ovr=ovr,
                pac=pac, sho=sho, pas=pas, dri=dri, def_=defd, phy=phy,
            )
            count += 1
    print(f"  {path.name}: {count} rows matched")
    return count

def kaggle_download(dataset, dest):
    dest = Path(dest)
    dest.mkdir(exist_ok=True)
    print(f"Downloading {dataset}...")
    cmd_base = ["datasets", "download", "-d", dataset, "-p", str(dest), "--unzip"]
    # Try three invocation styles: kaggle CLI, python -m kaggle, kaggle Python API
    for cmd in (
        ["kaggle"] + cmd_base,
        [sys.executable, "-m", "kaggle"] + cmd_base,
    ):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if r.returncode == 0:
                csvs = list(dest.rglob("*.csv"))
                print(f"  [OK] {len(csvs)} CSV(s) in {dest}")
                return csvs
            # Non-zero exit — print stderr and try next invocation style
            print(f"  ✗ {' '.join(cmd[:2])}: {r.stderr.strip()[:200]}")
        except FileNotFoundError:
            pass  # command not found, try next
        except subprocess.TimeoutExpired:
            print("  ✗ Timed out after 10 min")
            return []
    # Last resort: try importing kaggle directly as a Python library
    try:
        import kaggle as kg
        kg.api.authenticate()
        kg.api.dataset_download_files(dataset, path=str(dest), unzip=True)
        csvs = list(dest.rglob("*.csv"))
        if csvs:
            print(f"  [OK] {len(csvs)} CSV(s) via kaggle Python API")
            return csvs
    except Exception as e:
        print(f"  ✗ kaggle Python API: {e}")
    print(f"  Could not download {dataset}")
    return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", nargs="*", help="One or more FIFA player CSVs")
    ap.add_argument("--download", action="store_true", help="Download via Kaggle API")
    ap.add_argument("--out", default=str(OUT_FILE))
    args = ap.parse_args()

    csv_paths = [Path(p) for p in (args.csv or [])]

    if args.download or not csv_paths:
        # Download each dataset into its own subfolder, then merge all CSVs.
        # Process oldest→newest so later years overwrite stats for the same player.
        DATASETS = [
            # (kaggle_id,              subfolder,  description)
            ("joebeachcapital/fifa-players",                        "15to24", "FIFA 15–24"),
            ("nyagami/ea-sports-fc-25-database-ratings-and-stats",  "fc25",   "EA FC 25"),
            ("rovnez/fc-26-fifa-26-player-data",                    "fc26",   "EA FC 26"),
        ]
        all_csvs = []
        any_success = False
        for dataset, subfolder, label in DATASETS:
            dest = DATA_DIR / subfolder
            found = kaggle_download(dataset, dest)
            if found:
                any_success = True
                all_csvs.extend(found)
            else:
                print(f"  (skipping {label} — download failed)")

        if all_csvs:
            csv_paths = all_csvs
        elif not any_success:
            print("\n─ Could not auto-download ─────────────────────────────────────")
            print("Set up Kaggle API:  https://www.kaggle.com/docs/api")
            print("  pip install kaggle")
            print("  Place kaggle.json in ~/.kaggle/  (or %USERPROFILE%\\.kaggle\\)")
            print("\nOr download manually and run:")
            print("  FIFA 15–24 : https://www.kaggle.com/datasets/joebeachcapital/fifa-players")
            print("  EA FC 25   : https://www.kaggle.com/datasets/nyagami/ea-sports-fc-25-database-ratings-and-stats")
            print("  EA FC 26   : https://www.kaggle.com/datasets/rovnez/fc-26-fifa-26-player-data")
            print("\n  python process_fifa.py --csv players_24.csv fc25_male_players.csv fc26_players.csv")
            sys.exit(1)

    print(f"\nProcessing {len(csv_paths)} file(s)...")
    db = {}
    for p in sorted(csv_paths):
        process_csv(p, db)

    # Build output — one entry per (player, year); d = the FIFA season year
    out = []
    for entry in db.values():
        out.append({
            "n":   entry["name"],
            "p":   entry["pos"],
            "b":   entry["born"],
            "d":   entry["yr"],   # d = FIFA season year (2014=FIFA15, 2018=FIFA19…)
            "c":   entry["club"],
            "l":   entry["league"],
            "nat": entry["nat"],
            "o":   entry["ovr"],  # FIFA overall rating for this season
            "pac": entry["pac"], "sho": entry["sho"], "pas": entry["pas"],
            "dri": entry["dri"], "def": entry["def_"], "phy": entry["phy"],
        })

    out.sort(key=lambda x: (x["d"], x["l"], x["c"], x["n"]))

    yrs = [p["d"] for p in out]
    yr_range = f"{min(yrs)}–{max(yrs)}" if yrs else "unknown"
    lines = [
        "// FIFA / EA FC player data — generated by process_fifa.py",
        f"// {len(out)} player-seasons across 5 leagues  |  years {yr_range}",
        "// Keys: n=name p=pos b=born d=season_year c=club l=league nat=nationality",
        "//       o=overall pac sho pas dri def phy",
        "var FIFA_PLAYERS=["
    ]
    for p in out:
        lines.append(
            f'{{n:{json.dumps(p["n"],ensure_ascii=False)},p:"{p["p"]}",'
            f'b:{p["b"]},d:{p["d"]},c:"{p["c"]}",l:"{p["l"]}",nat:"{p["nat"]}",'
            f'o:{p["o"]},pac:{p["pac"]},sho:{p["sho"]},pas:{p["pas"]},'
            f'dri:{p["dri"]},def:{p["def"]},phy:{p["phy"]}}},'
        )
    lines.append("];")

    out_path = Path(args.out)
    out_path.write_text("\n".join(lines), encoding="utf-8")

    unique_players = len({(p["n"], p["b"]) for p in out})
    unique_years   = sorted({p["d"] for p in out})
    print(f"\n[OK] {len(out)} player-seasons ({unique_players} unique players) written to {out_path}")
    print(f"   Years covered: {unique_years}")
    league_counts = Counter(p["l"] for p in out)
    club_counts   = Counter(p["c"] for p in out)
    for lg, n in sorted(league_counts.items()):
        print(f"   {lg}: {n} player-seasons")
    print(f"\n   Clubs with data: {len(club_counts)}")
    missing = [t for t in CLUB_MAP.values() if t not in club_counts]
    if missing:
        print(f"   No players found for: {sorted(set(missing))}")

if __name__ == "__main__":
    main()
