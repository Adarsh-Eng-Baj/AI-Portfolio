/**
 * i18n.js — Internationalization system.
 * Supports English and Hindi translations via JSON files.
 */

const I18n = (() => {
  let currentLang = localStorage.getItem('portfolio_lang') || 'en';
  let translations = {};

  /** Load a language JSON file from /translations/ */
  async function loadLanguage(lang) {
    try {
      const cacheBuster = Date.now();
      const res = await fetch(`/translations/${lang}.json?v=${cacheBuster}`);
      if (!res.ok) throw new Error(`Failed to load ${lang}.json`);
      translations = await res.json();
      currentLang = lang;
      localStorage.setItem('portfolio_lang', lang);
      _applyTranslations();
      _updateToggleButton();
    } catch (err) {
      console.warn('i18n: Could not load translations for', lang, err);
    }
  }

  /** Apply translations to all elements with data-i18n attribute */
  function _applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = _getTranslation(key);
      if (text) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = text;
        } else {
          el.textContent = text;
        }
      }
    });

    // Update lang attribute on html element
    document.documentElement.lang = currentLang;
  }

  /** Get a translation by dot-notation key e.g. "nav.home" */
  function _getTranslation(key) {
    return key.split('.').reduce((obj, k) => obj && obj[k], translations) || key;
  }

  /** Update the language toggle button text */
  function _updateToggleButton() {
    const btn = document.getElementById('lang-toggle-btn');
    if (btn) btn.textContent = currentLang === 'en' ? 'हिं' : 'EN';
  }

  /** Toggle between English and Hindi */
  function toggle() {
    const newLang = currentLang === 'en' ? 'hi' : 'en';
    loadLanguage(newLang);
  }

  /** Get current language */
  function getLanguage() { return currentLang; }

  /** Get a translation value directly in JS */
  function t(key) { return _getTranslation(key); }

  // Initialize on load
  async function init() {
    await loadLanguage(currentLang);
  }

  return { init, toggle, getLanguage, t, loadLanguage };
})();

window.I18n = I18n;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  I18n.init();

  // Bind language toggle button
  const langBtn = document.getElementById('lang-toggle-btn');
  if (langBtn) langBtn.addEventListener('click', I18n.toggle);
});
