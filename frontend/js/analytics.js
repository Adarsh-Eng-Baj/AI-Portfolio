/**
 * analytics.js — Visitor tracking for the portfolio frontend.
 * Tracks page visits and duration, sends to the backend.
 */

const Analytics = (() => {
  // Generate / retrieve a persistent session ID
  function _getSessionId() {
    let sid = sessionStorage.getItem('portfolio_sid');
    if (!sid) {
      sid = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('portfolio_sid', sid);
    }
    return sid;
  }

  // Track page entry time
  const _pageStart = Date.now();
  const _page = window.location.pathname || '/';
  const _sessionId = _getSessionId();

  /** Send a tracking event to the backend */
  async function track(durationSec = 0) {
    try {
      await fetch(`${window.API_BASE_URL || 'http://localhost:5000/api'}/analytics/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page: _page,
          session_id: _sessionId,
          referrer: document.referrer || '',
          duration: durationSec,
        }),
        keepalive: true,  // Ensures the request completes even if page unloads
      });
    } catch (_) {
      // Fail silently — analytics should never break the site
    }
  }

  /** Initialize analytics tracking on page load */
  function init() {
    // Track page entry
    track(0);

    // Track duration on page unload
    window.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        const duration = Math.round((Date.now() - _pageStart) / 1000);
        track(duration);
      }
    });

    window.addEventListener('pagehide', () => {
      const duration = Math.round((Date.now() - _pageStart) / 1000);
      track(duration);
    });
  }

  return { init };
})();

// Auto-initialize
document.addEventListener('DOMContentLoaded', Analytics.init);
