/**
 * error_handler.js — Global Real-Time Error Tracking
 * Catches unhandled browser errors and promise rejections.
 */

const ErrorHandler = (() => {
  // Config
  const SHOW_TOASTS = true; // Set to true to show UI notifications for errors

  function init() {
    // 1. Catch synchronous global errors (Syntax, DOM, undefined, etc.)
    window.onerror = function (message, source, lineno, colno, error) {
      _handleError('SYNC_ERROR', message, source, lineno, colno, error);
      return false; // Let default browser console log also run
    };

    // 2. Catch asynchronous promise rejections (Fetch failures, async crashes)
    window.addEventListener('unhandledrejection', function (event) {
      _handleError('UNHANDLED_REJECTION', event.reason?.message || event.reason, 'Promise', 0, 0, event.reason);
    });

    console.log('[ErrorHandler] Active and watching for real-time errors.');
  }

  function _handleError(type, message, source, lineno, colno, errorObj) {
    // Format error log
    const errorDetails = {
      type: type,
      message: message,
      source: source,
      line: lineno,
      column: colno,
      timestamp: new Date().toISOString(),
      stack: errorObj?.stack || 'No stack trace available'
    };

    // Log securely to console
    console.error('🚨 [Global Error Tracked]:', errorDetails);

    // Optionally display toast to user (if Toast is defined)
    if (SHOW_TOASTS && window.Toast) {
      // Don't show toast for benign network errors so it doesn't spam users
      if (!message.toString().includes('Network error')) {
        Toast.error('System Error Recorded', 'An unexpected error occurred. We have logged it.');
      }
    }

    // Future enhancement: Send `errorDetails` to backend via API Fetch here
    // API.analytics.trackError(errorDetails);
  }

  // Expose a manual error triggering function for testing
  function triggerManualError() {
    throw new Error('This is a manually triggered real-time error test.');
  }

  return { init, triggerManualError };
})();

// Auto-initialize prior to other scripts loading
document.addEventListener('DOMContentLoaded', ErrorHandler.init);
