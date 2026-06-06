/**
 * Blog JavaScript — Thomas Pasley
 * Handles: nav scroll/toggle, listing page render, viz panel
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        initNav();
        initListingPage();
        initVizPanel();
    });

    // ==================== NAV ====================
    function initNav() {
        const nav = document.getElementById('main-nav');
        const toggle = document.getElementById('navToggle');
        const menu = document.getElementById('navMenu');
        if (!nav) return;

        window.addEventListener('scroll', function () {
            nav.classList.toggle('scrolled', window.scrollY > 80);
        });

        if (toggle && menu) {
            toggle.addEventListener('click', function () {
                menu.classList.toggle('active');
                toggle.classList.toggle('active');
            });

            menu.querySelectorAll('.nav-link').forEach(function (link) {
                link.addEventListener('click', function () {
                    menu.classList.remove('active');
                    toggle.classList.remove('active');
                });
            });
        }
    }

    // ==================== LISTING PAGE ====================
    function initListingPage() {
        const root = document.getElementById('postsRoot');
        if (!root || typeof BLOG_POSTS === 'undefined') return;

        const posts = [...BLOG_POSTS]; // already newest-first in posts.js
        const featured = posts.find(function (p) { return p.featured; });
        const others = posts.filter(function (p) { return !p.featured; });

        // Render featured card
        const featuredZone = document.getElementById('featuredZone');
        if (featuredZone && featured) {
            featuredZone.innerHTML = buildFeaturedCard(featured);
        }

        // Render regular cards
        const regularGrid = document.getElementById('regularGrid');
        if (regularGrid) {
            regularGrid.innerHTML = others.map(buildCard).join('');
            if (others.length === 0) regularGrid.style.display = 'none';
        }

        // Build tag filter from all posts
        buildTagFilter(posts);
    }

    function buildTagFilter(posts) {
        const bar = document.getElementById('tagFilter');
        if (!bar) return;

        const allTags = [];
        posts.forEach(function (p) {
            p.tags.forEach(function (t) {
                if (!allTags.includes(t)) allTags.push(t);
            });
        });

        const buttons = ['<button class="filter-btn active" data-tag="all">All</button>'];
        allTags.forEach(function (t) {
            buttons.push('<button class="filter-btn" data-tag="' + escHtml(t) + '">' + escHtml(t) + '</button>');
        });
        bar.innerHTML = buttons.join('');

        // Filter logic
        bar.addEventListener('click', function (e) {
            const btn = e.target.closest('.filter-btn');
            if (!btn) return;
            const tag = btn.dataset.tag;

            bar.querySelectorAll('.filter-btn').forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');

            const cards = document.querySelectorAll('.post-card[data-tags]');
            let visible = 0;
            cards.forEach(function (card) {
                const cardTags = card.dataset.tags.split(',').map(function (t) { return t.trim().toLowerCase(); });
                const show = tag === 'all' || cardTags.includes(tag.toLowerCase());
                card.style.display = show ? '' : 'none';
                if (show) visible++;
            });

            const empty = document.getElementById('postsEmpty');
            if (empty) empty.classList.toggle('visible', visible === 0);
        });
    }

    function buildFeaturedCard(post) {
        const href = 'posts/' + escHtml(post.slug) + '.html';
        return [
            '<a href="' + href + '" class="post-card featured" data-tags="' + escHtml(post.tags.join(',')) + '" style="text-decoration:none">',
            '  <div class="card-visual" aria-hidden="true">' + pipelineIconSVG() + '</div>',
            '  <div class="card-body">',
            '    <span class="card-featured-label">Featured Post</span>',
            '    <div class="card-meta">',
            '      <span><i class="fas fa-calendar-alt"></i> ' + formatDate(post.date) + '</span>',
            '      <span><i class="fas fa-clock"></i> ' + post.readTime + ' min read</span>',
            '    </div>',
            '    <h2 class="card-title">' + escHtml(post.title) + '</h2>',
            '    <p class="card-excerpt">' + escHtml(post.description) + '</p>',
            '    <div class="card-tags">' + post.tags.map(function (t) { return '<span class="card-tag">' + escHtml(t) + '</span>'; }).join('') + '</div>',
            '    <span class="card-link">Read article <i class="fas fa-arrow-right"></i></span>',
            '  </div>',
            '</a>'
        ].join('\n');
    }

    function buildCard(post) {
        const href = 'posts/' + escHtml(post.slug) + '.html';
        return [
            '<a href="' + href + '" class="post-card" data-tags="' + escHtml(post.tags.join(',')) + '" style="text-decoration:none">',
            '  <div class="card-body">',
            '    <div class="card-meta">',
            '      <span><i class="fas fa-calendar-alt"></i> ' + formatDate(post.date) + '</span>',
            '      <span><i class="fas fa-clock"></i> ' + post.readTime + ' min</span>',
            '    </div>',
            '    <h2 class="card-title">' + escHtml(post.title) + '</h2>',
            '    <p class="card-excerpt">' + escHtml(post.description) + '</p>',
            '    <div class="card-tags">' + post.tags.map(function (t) { return '<span class="card-tag">' + escHtml(t) + '</span>'; }).join('') + '</div>',
            '    <span class="card-link">Read article <i class="fas fa-arrow-right"></i></span>',
            '  </div>',
            '</a>'
        ].join('\n');
    }

    // ==================== VIZ PANEL ====================
    function initVizPanel() {
        const panel = document.getElementById('vizPanel');
        if (!panel) return;

        const pullTab = panel.querySelector('.viz-pull-tab');
        const closeBtn = panel.querySelector('.viz-close-btn');
        const backdrop = document.getElementById('vizBackdrop');
        const tabBtns = panel.querySelectorAll('.viz-tab-btn');
        const panes = panel.querySelectorAll('.viz-pane');

        function open() {
            panel.classList.add('open');
            if (backdrop) backdrop.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        function close() {
            panel.classList.remove('open');
            if (backdrop) backdrop.classList.remove('active');
            document.body.style.overflow = '';
        }

        if (pullTab) pullTab.addEventListener('click', function () {
            panel.classList.contains('open') ? close() : open();
        });

        if (closeBtn) closeBtn.addEventListener('click', close);
        if (backdrop) backdrop.addEventListener('click', close);

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && panel.classList.contains('open')) close();
        });

        tabBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                const target = btn.dataset.pane;
                tabBtns.forEach(function (b) { b.classList.remove('active'); });
                panes.forEach(function (p) { p.classList.remove('active'); });
                btn.classList.add('active');
                const pane = panel.querySelector('#viz-' + target);
                if (pane) pane.classList.add('active');
            });
        });
    }

    // ==================== HELPERS ====================
    function formatDate(iso) {
        return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    }

    function escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function pipelineIconSVG() {
        return '<svg viewBox="0 0 200 240" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
            '<rect x="30" y="10" width="140" height="38" rx="6" fill="rgba(16,185,129,0.15)" stroke="#10b981" stroke-width="1.2"/>' +
            '<text x="100" y="34" text-anchor="middle" fill="#34d399" font-size="11" font-weight="600" font-family="Fira Code,monospace">Raw OHLCV</text>' +
            '<line x1="100" y1="48" x2="100" y2="66" stroke="#404040" stroke-width="1.5" marker-end="url(#arr)"/>' +
            '<rect x="30" y="66" width="140" height="38" rx="6" fill="rgba(16,185,129,0.1)" stroke="#10b981" stroke-width="1.2"/>' +
            '<text x="100" y="90" text-anchor="middle" fill="#34d399" font-size="11" font-weight="600" font-family="Fira Code,monospace">Lag Features</text>' +
            '<line x1="100" y1="104" x2="100" y2="122" stroke="#404040" stroke-width="1.5" marker-end="url(#arr)"/>' +
            '<rect x="30" y="122" width="140" height="38" rx="6" fill="rgba(16,185,129,0.1)" stroke="#10b981" stroke-width="1.2"/>' +
            '<text x="100" y="146" text-anchor="middle" fill="#6ee7b7" font-size="11" font-weight="600" font-family="Fira Code,monospace">Rolling Stats</text>' +
            '<line x1="100" y1="160" x2="100" y2="178" stroke="#404040" stroke-width="1.5" marker-end="url(#arr)"/>' +
            '<rect x="30" y="178" width="140" height="38" rx="6" fill="rgba(245,158,11,0.1)" stroke="#f59e0b" stroke-width="1.2"/>' +
            '<text x="100" y="202" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="600" font-family="Fira Code,monospace">Tech Indicators</text>' +
            '<line x1="100" y1="216" x2="100" y2="228" stroke="#404040" stroke-width="1.5" marker-end="url(#arr)"/>' +
            '<rect x="30" y="228" rx="6" width="140" height="0.5" fill="none"/>' +
            '<defs><marker id="arr" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L8 4L0 8z" fill="#555555"/></marker></defs>' +
            '</svg>';
    }

})();
