/**
 * Complete Redesign - Interactive Features JavaScript
 * Thomas Pasley - Data Scientist Portfolio
 */

(function() {
    'use strict';

    // ==================== DOM READY ====================
    document.addEventListener('DOMContentLoaded', function() {
        initNavigation();
        initScrollEffects();
        initStatsCounter();
        initSkillBars();
        initIntersectionObserver();
        initTypingEffect();
    });

    // ==================== NAVIGATION ====================
    function initNavigation() {
        const nav = document.getElementById('main-nav');
        const navToggle = document.getElementById('navToggle');
        const navMenu = document.getElementById('navMenu');
        const navLinks = document.querySelectorAll('.nav-link');

        // Mobile menu toggle
        if (navToggle) {
            navToggle.addEventListener('click', function() {
                navMenu.classList.toggle('active');
                this.classList.toggle('active');
            });
        }

        // Close mobile menu when clicking a link
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                if (navToggle) {
                    navToggle.classList.remove('active');
                }
            });
        });

        // Smooth scroll for navigation links
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetSection = document.querySelector(targetId);

                if (targetSection) {
                    const offsetTop = targetSection.offsetTop - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Active navigation on scroll
        window.addEventListener('scroll', function() {
            // Add shadow to nav on scroll
            if (window.scrollY > 100) {
                nav.classList.add('scrolled');
            } else {
                nav.classList.remove('scrolled');
            }

            // Update active link based on scroll position
            let current = '';
            const sections = document.querySelectorAll('section[id]');

            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;

                if (window.scrollY >= (sectionTop - 150)) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${current}`) {
                    link.classList.add('active');
                }
            });
        });
    }

    // ==================== SCROLL EFFECTS ====================
    function initScrollEffects() {
        // Parallax effect for hero orbs
        const orbs = document.querySelectorAll('.gradient-orb');

        window.addEventListener('scroll', function() {
            const scrolled = window.scrollY;

            orbs.forEach((orb, index) => {
                const speed = 0.5 + (index * 0.2);
                orb.style.transform = `translateY(${scrolled * speed}px)`;
            });
        });
    }

    // ==================== STATS COUNTER ====================
    function initStatsCounter() {
        const stats = document.querySelectorAll('.stat-number');
        let animated = false;

        const animateStats = () => {
            stats.forEach(stat => {
                const target = parseInt(stat.getAttribute('data-target'));
                let count = 0;
                const increment = target / 50; // Adjust speed

                const updateCount = () => {
                    if (count < target) {
                        count += increment;
                        stat.textContent = Math.ceil(count);
                        setTimeout(updateCount, 30);
                    } else {
                        stat.textContent = target;
                    }
                };

                updateCount();
            });
        };

        // Trigger animation when stats section is in view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !animated) {
                    animateStats();
                    animated = true;
                }
            });
        }, { threshold: 0.5 });

        const statsSection = document.querySelector('.stats-section');
        if (statsSection) {
            observer.observe(statsSection);
        }
    }

    // ==================== SKILL BARS ANIMATION ====================
    function initSkillBars() {
        const skillBars = document.querySelectorAll('.skill-progress');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const progress = bar.getAttribute('data-progress');
                    bar.style.width = progress + '%';
                }
            });
        }, { threshold: 0.5 });

        skillBars.forEach(bar => {
            observer.observe(bar);
        });
    }

    // ==================== INTERSECTION OBSERVER ====================
    function initIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observe all major sections and cards
        const elementsToObserve = document.querySelectorAll(`
            .stat-item,
            .about-text,
            .about-image,
            .skill-category,
            .timeline-item,
            .education-card,
            .cert-card,
            .contact-method
        `);

        elementsToObserve.forEach(el => {
            observer.observe(el);
        });
    }

    // ==================== TYPING EFFECT ====================
    function initTypingEffect() {
        const heroTitle = document.querySelector('.hero-title');
        if (!heroTitle) return;

        const originalText = heroTitle.textContent;
        heroTitle.textContent = '';
        let index = 0;

        function type() {
            if (index < originalText.length) {
                heroTitle.textContent += originalText.charAt(index);
                index++;
                setTimeout(type, 100);
            } else {
                // Add blinking cursor after typing is done
                heroTitle.classList.add('typing-done');
            }
        }

        // Start typing after a short delay
        setTimeout(type, 1500);
    }

    // ==================== BACK TO TOP BUTTON ====================
    function initBackToTop() {
        // Create button
        const button = document.createElement('button');
        button.className = 'back-to-top';
        button.innerHTML = '<i class="fas fa-arrow-up"></i>';
        button.setAttribute('aria-label', 'Back to top');
        document.body.appendChild(button);

        // Show/hide on scroll
        window.addEventListener('scroll', () => {
            if (window.scrollY > 500) {
                button.classList.add('visible');
            } else {
                button.classList.remove('visible');
            }
        });

        // Scroll to top on click
        button.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Initialize back to top button
    initBackToTop();

    // ==================== CURSOR TRAIL EFFECT ====================
    function initCursorTrail() {
        let mouseX = 0;
        let mouseY = 0;
        let trailX = 0;
        let trailY = 0;

        const cursor = document.createElement('div');
        cursor.className = 'cursor-trail';
        document.body.appendChild(cursor);

        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        function animateTrail() {
            trailX += (mouseX - trailX) * 0.1;
            trailY += (mouseY - trailY) * 0.1;

            cursor.style.left = trailX + 'px';
            cursor.style.top = trailY + 'px';

            requestAnimationFrame(animateTrail);
        }

        animateTrail();
    }

    // Initialize cursor trail (optional - uncomment if desired)
    // initCursorTrail();

    // ==================== FADE IN ANIMATION CLASS ====================
    // Add CSS for fade-in animation
    const style = document.createElement('style');
    style.textContent = `
        .fade-in {
            animation: fadeInUp 0.8s ease forwards;
        }

        .back-to-top {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary), var(--primary-light));
            color: white;
            border: none;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        }

        .back-to-top.visible {
            opacity: 1;
            visibility: visible;
        }

        .back-to-top:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.6);
        }

        .back-to-top i {
            font-size: 1.25rem;
        }

        .cursor-trail {
            position: fixed;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: var(--primary);
            pointer-events: none;
            z-index: 9999;
            opacity: 0.5;
            filter: blur(2px);
        }

        .typing-done::after {
            content: '';
            display: inline-block;
            width: 2px;
            height: 1.2em;
            background: var(--primary);
            margin-left: 0.2rem;
            animation: blink 1s step-end infinite;
        }

        @keyframes blink {
            50% { opacity: 0; }
        }

        @media (max-width: 768px) {
            .back-to-top {
                bottom: 1rem;
                right: 1rem;
                width: 45px;
                height: 45px;
            }

            .cursor-trail {
                display: none;
            }
        }
    `;
    document.head.appendChild(style);

    // ==================== PERFORMANCE OPTIMIZATION ====================
    // Debounce function for scroll events
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Apply debounce to scroll-heavy operations
    window.addEventListener('scroll', debounce(function() {
        // Additional scroll operations can go here
    }, 10));

    // ==================== EASTER EGG ====================
    // Konami code easter egg
    let konamiCode = [];
    const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑ ↑ ↓ ↓ ← → ← → B A

    document.addEventListener('keydown', (e) => {
        konamiCode.push(e.keyCode);
        konamiCode.splice(-konamiSequence.length - 1, konamiCode.length - konamiSequence.length);

        if (konamiCode.join('').includes(konamiSequence.join(''))) {
            activateEasterEgg();
        }
    });

    function activateEasterEgg() {
        // Add a fun animation or effect
        document.body.style.animation = 'rainbow 2s infinite';

        const style = document.createElement('style');
        style.textContent = `
            @keyframes rainbow {
                0% { filter: hue-rotate(0deg); }
                100% { filter: hue-rotate(360deg); }
            }
        `;
        document.head.appendChild(style);

        setTimeout(() => {
            document.body.style.animation = '';
        }, 5000);
    }

    // ==================== CONSOLE MESSAGE ====================
    console.log('%c👋 Hello there!', 'font-size: 20px; font-weight: bold; color: #6366f1;');
    console.log('%c🚀 Thanks for checking out the code!', 'font-size: 14px; color: #cbd5e1;');
    console.log('%c💼 Looking for a data scientist? Let\'s connect!', 'font-size: 14px; color: #10b981;');

})();
