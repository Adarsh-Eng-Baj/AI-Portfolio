/**
 * maintenance-check.js
 * Included in the head of all pages to check site status.
 * Redirects to maintenance.html if maintenance mode is enabled.
 */
(async function() {
    // 1. Skip check if already on maintenance page or admin pages
    const path = window.location.pathname;
    if (path.includes('maintenance.html') || path.includes('/admin/')) {
        return;
    }

    try {
        // We use fetch direct here or window.API if available
        // Note: API might not be initialized yet if this script is in <head>
        // so we'll fetch from the known endpoint
        const apiBase = window.API_BASE_URL || 'http://localhost:5000/api';
        const response = await fetch(`${apiBase}/settings/public`);
        
        if (response.ok) {
            const settings = await response.json();
            
            if (settings.maintenance_mode === true) {
                // If logged in as admin, ALLOW access
                const token = localStorage.getItem('portfolio_token');
                if (token) {
                    try {
                        // Optional: Verify token role by calling /auth/me
                        // But for speed, we can just check if token exists
                        // and let the actual API calls handle permission errors.
                        // For a better UX, we'll verify it's an admin.
                        const authRes = await fetch(`${apiBase}/auth/me`, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        const userData = await authRes.json();
                        if (userData.role === 'admin') {
                            console.log("Maintenance mode active, but admin access granted.");
                            return; 
                        }
                    } catch (err) {
                        console.error("Auth verification failed during maintenance check", err);
                    }
                }
                
                // Not an admin or not logged in, redirect to maintenance page
                window.location.href = '/maintenance.html';
            }
        }
    } catch (error) {
        console.error("Maintenance check failed:", error);
    }
})();
