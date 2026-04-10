/**
 * main.js — Core utilities: navbar, theme, toast, scroll animations, typing effect.
 * Loaded on every page.
 */

// ═══════════════════════════════════════════
// 1. THEME MANAGER
// ═══════════════════════════════════════════
const Theme = (() => {
  const STORAGE_KEY = 'portfolio_theme';

  function get() { return localStorage.getItem(STORAGE_KEY) || 'dark'; }

  function set(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
  }

  function toggle() { set(get() === 'dark' ? 'light' : 'dark'); }

  function init() {
    set(get());
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) btn.addEventListener('click', toggle);
  }

  return { init, toggle, get };
})();


// ═══════════════════════════════════════════
// 2. NAVBAR
// ═══════════════════════════════════════════
const Navbar = (() => {
  function init() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    // Scroll effect
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });

    // Hamburger for mobile
    const hamburger = document.getElementById('nav-hamburger');
    const navLinks = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
      hamburger.addEventListener('click', () => {
        navLinks.classList.toggle('open');
        hamburger.classList.toggle('open');
      });
      // Close menu on link click
      navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => navLinks.classList.remove('open'));
      });
    }

    // Mark active link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link[href]').forEach(link => {
      const href = link.getAttribute('href');
      if (currentPath.includes(href) && href !== '/') {
        link.classList.add('active');
      } else if (href === 'index.html' && (currentPath === '/' || currentPath.endsWith('index.html'))) {
        link.classList.add('active');
      }
    });
  }

  return { init };
})();


// ═══════════════════════════════════════════
// 3. TOAST NOTIFICATIONS
// ═══════════════════════════════════════════
const Toast = (() => {
  let container;

  function _ensureContainer() {
    if (!container) {
      container = document.getElementById('toast-container');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
      }
    }
    return container;
  }

  const ICONS = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };

  function show(type, title, message, duration = 4000) {
    const c = _ensureContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${ICONS[type] || 'ℹ️'}</span>
      <div class="toast-body">
        <div class="toast-title">${title}</div>
        ${message ? `<div class="toast-msg">${message}</div>` : ''}
      </div>
      <button onclick="this.closest('.toast').remove()" style="background:none;color:var(--clr-text-muted);font-size:1.2rem;padding:0 4px;">×</button>
    `;
    c.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 350);
    }, duration);
  }

  return {
    success: (title, msg) => show('success', title, msg),
    error:   (title, msg) => show('error',   title, msg),
    info:    (title, msg) => show('info',    title, msg),
    warning: (title, msg) => show('warning', title, msg),
  };
})();


// ═══════════════════════════════════════════
// 4. SCROLL ANIMATIONS (IntersectionObserver)
// ═══════════════════════════════════════════
const ScrollAnimations = (() => {
  function init() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            e.target.classList.add('visible');
            // Animate skill bars inside
            e.target.querySelectorAll('.skill-bar-fill').forEach(bar => {
              bar.style.width = bar.dataset.pct + '%';
            });
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));

    // Counter animation for hero stats
    document.querySelectorAll('[data-count]').forEach(el => {
      const observer2 = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
          animateCounter(el);
          observer2.disconnect();
        }
      }, { threshold: 0.5 });
      observer2.observe(el);
    });
  }

  function animateCounter(el) {
    const target = parseInt(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    let current = 0;
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = current + suffix;
      if (current >= target) clearInterval(timer);
    }, 20);
  }

  return { init };
})();


// ═══════════════════════════════════════════
// 5. TYPING EFFECT
// ═══════════════════════════════════════════
function startTypingEffect(elementId, phrases, speed = 80) {
  const el = document.getElementById(elementId);
  if (!el) return;

  let phraseIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let isPaused = false;

  function type() {
    const phrase = phrases[phraseIndex % phrases.length];

    if (!isDeleting) {
      el.textContent = phrase.substring(0, charIndex + 1);
      charIndex++;
      if (charIndex === phrase.length) {
        isPaused = true;
        setTimeout(() => { isPaused = false; isDeleting = true; }, 2000);
      }
    } else {
      el.textContent = phrase.substring(0, charIndex - 1);
      charIndex--;
      if (charIndex === 0) {
        isDeleting = false;
        phraseIndex++;
      }
    }

    const delay = isPaused ? 2000 : isDeleting ? speed / 2 : speed;
    if (!isPaused) setTimeout(type, delay);
  }

  setTimeout(type, 500);
}


// ═══════════════════════════════════════════
// 6. FORM VALIDATION HELPER
// ═══════════════════════════════════════════
function validateForm(formEl) {
  let isValid = true;

  formEl.querySelectorAll('[data-required]').forEach(input => {
    const errEl = formEl.querySelector(`[data-error="${input.name || input.id}"]`);
    if (!input.value.trim()) {
      input.classList.add('error');
      if (errEl) errEl.textContent = input.dataset.requiredMsg || 'This field is required';
      isValid = false;
    } else {
      input.classList.remove('error');
      if (errEl) errEl.textContent = '';
    }
  });

  // Email fields
  formEl.querySelectorAll('input[type="email"]').forEach(input => {
    const errEl = formEl.querySelector(`[data-error="${input.name || input.id}"]`);
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (input.value && !emailRegex.test(input.value)) {
      input.classList.add('error');
      if (errEl) errEl.textContent = 'Please enter a valid email address';
      isValid = false;
    }
  });

  return isValid;
}


// ═══════════════════════════════════════════
// 7. UTILITY FUNCTIONS
// ═══════════════════════════════════════════

/** Format a date string nicely */
function formatDate(isoString) {
  if (!isoString) return '';
  return new Date(isoString).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric'
  });
}

/** Truncate text to N chars */
function truncate(text, n = 120) {
  if (!text) return '';
  return text.length > n ? text.substring(0, n) + '…' : text;
}

/** Debounce a function */
function debounce(fn, delay = 300) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn.apply(this, args), delay);
  };
}

/** Safely set innerText without XSS */
function safeText(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

// ── Common Navbar HTML ─────────────────────────────────
function renderNavbar(activePage = '') {
  const navHtml = `
    <nav class="navbar" id="main-navbar">
      <div class="nav-container">
        <a href="/index.html" class="nav-logo">AS.</a>
        <ul class="nav-links" id="nav-links">
          <li><a href="/index.html" class="nav-link ${activePage==='home'?'active':''}" data-i18n="nav.home">Home</a></li>
          <li><a href="/about.html" class="nav-link ${activePage==='about'?'active':''}" data-i18n="nav.about">About</a></li>
          <li><a href="/projects.html" class="nav-link ${activePage==='projects'?'active':''}" data-i18n="nav.projects">Projects</a></li>
          <li><a href="/skills.html" class="nav-link ${activePage==='skills'?'active':''}" data-i18n="nav.skills">Skills</a></li>
          <li><a href="/blog.html" class="nav-link ${activePage==='blog'?'active':''}" data-i18n="nav.blog">Blog</a></li>
          <li><a href="/contact.html" class="nav-link ${activePage==='contact'?'active':''}" data-i18n="nav.contact">Contact</a></li>
        </ul>
        <div class="nav-actions">
          <button class="lang-toggle" id="lang-toggle-btn" aria-label="Toggle language">हिं</button>
          <button class="theme-toggle" id="theme-toggle-btn" aria-label="Toggle theme">☀️</button>
          <button class="nav-hamburger" id="nav-hamburger" aria-label="Toggle menu">
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>
    </nav>`;
  return navHtml;
}

// ── Common Footer HTML ─────────────────────────────────
function renderFooter() {
  return `
    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="footer-logo gradient-text">Adarsh Sutar</div>
            <p class="footer-desc">B.Tech CSE-AI student passionate about AI/ML, Full-Stack Development, and building impactful tech solutions.</p>
            <div class="footer-social">
              <a href="https://github.com/adarshsutar" target="_blank" class="social-link" aria-label="GitHub">🐙</a>
              <a href="https://linkedin.com/in/adarshsutar" target="_blank" class="social-link" aria-label="LinkedIn">💼</a>
              <a href="mailto:admin@portfolio.com" class="social-link" aria-label="Email">📧</a>
              <a href="https://twitter.com/adarshsutar" target="_blank" class="social-link" aria-label="Twitter">🐦</a>
            </div>
          </div>
          <div>
            <h4 class="footer-col-title" data-i18n="footer.navigate">Navigate</h4>
            <nav class="footer-links">
              <a href="/index.html" class="footer-link" data-i18n="nav.home">Home</a>
              <a href="/about.html" class="footer-link" data-i18n="nav.about">About</a>
              <a href="/projects.html" class="footer-link" data-i18n="nav.projects">Projects</a>
              <a href="/skills.html" class="footer-link" data-i18n="nav.skills">Skills</a>
            </nav>
          </div>
          <div>
            <h4 class="footer-col-title" data-i18n="footer.connect">Connect</h4>
            <nav class="footer-links">
              <a href="/contact.html" class="footer-link" data-i18n="nav.contact">Contact</a>
              <a href="${window.API_BASE_URL || 'http://localhost:5000/api'}/resume/download" class="footer-link" data-i18n="footer.resume">Download Resume</a>
              <a href="/blog.html" class="footer-link" data-i18n="nav.blog">Blog</a>
              <a href="/admin/login.html" class="footer-link">Admin</a>
            </nav>
          </div>
        </div>
        <div class="footer-bottom">
          <p class="footer-copy">&copy; ${new Date().getFullYear()} Adarsh Dev. Built with ❤️ &amp; Python.</p>
          <p class="footer-copy" style="color:var(--clr-purple);">B.Tech CSE-AI • GIET Bhubaneswar</p>
        </div>
      </div>
    </footer>
    <div id="toast-container"></div>`;
}


// ═══════════════════════════════════════════
// SUCCESS ANIMATION — Myntra Style
// ═══════════════════════════════════════════
const SuccessAnim = (() => {
  const COLORS = ['#7c3aed','#2563eb','#06b6d4','#10b981','#f59e0b','#ec4899'];

  function _makeConfetti(container) {
    for (let i = 0; i < 24; i++) {
      const dot = document.createElement('div');
      dot.className = 'confetti-dot';
      dot.style.cssText = [
        `left: ${Math.random() * 100}%`,
        `top: ${Math.random() * 40}%`,
        `background: ${COLORS[i % COLORS.length]}`,
        `--delay: ${(Math.random() * 0.8).toFixed(2)}s`,
        `transform: rotate(${Math.random() * 360}deg)`,
      ].join(';');
      container.appendChild(dot);
    }
  }

  function show({ title = 'Success!', subtitle = '', badge = '', autoClose = 2500 } = {}) {
    // Remove existing overlay
    document.getElementById('success-anim-overlay')?.remove();

    const overlay = document.createElement('div');
    overlay.id = 'success-anim-overlay';
    overlay.className = 'success-overlay';
    overlay.innerHTML = `
      <div class="success-card">
        <div class="success-confetti" id="sa-confetti"></div>
        <div class="success-circle-wrap">
          <div class="success-ring"></div>
          <div class="success-ring"></div>
          <div class="success-circle-bg"></div>
          <svg class="success-check-svg" viewBox="0 0 56 56">
            <path class="success-check-path" d="M14 28 L23 38 L42 18" />
          </svg>
        </div>
        <h2 class="success-title">${title}</h2>
        ${subtitle ? `<p class="success-subtitle">${subtitle}</p>` : ''}
        ${badge ? `<span class="success-badge">${badge}</span>` : ''}
        <button class="success-close-btn" id="sa-close-btn">Continue →</button>
      </div>`;

    document.body.appendChild(overlay);
    _makeConfetti(overlay.querySelector('#sa-confetti'));

    // Trigger animation
    requestAnimationFrame(() => {
      requestAnimationFrame(() => { overlay.classList.add('show'); });
    });

    // Auto-close
    const timer = setTimeout(() => close(), autoClose);

    // Manual close
    overlay.querySelector('#sa-close-btn').addEventListener('click', () => {
      clearTimeout(timer);
      close();
    });
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) { clearTimeout(timer); close(); }
    });

    function close() {
      overlay.classList.remove('show');
      setTimeout(() => overlay.remove(), 400);
    }
  }

  return { show };
})();

// ─────────────────────────────────────────────
// INIT on DOM Ready
// ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();
  Navbar.init();
  ScrollAnimations.init();
});

// Expose globally
window.Toast = Toast;
window.formatDate = formatDate;
window.truncate = truncate;
window.debounce = debounce;
window.validateForm = validateForm;
window.startTypingEffect = startTypingEffect;
window.renderNavbar = renderNavbar;
window.renderFooter = renderFooter;
window.SuccessAnim = SuccessAnim;
