"""
run.py — Entry point for the Portfolio Flask application.
Run with: python run.py
"""

import os
from app import create_app

# Create the Flask app instance using the factory pattern
app = create_app()

if __name__ == '__main__':
    # Read port from environment (Render sets PORT automatically)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"[+] Portfolio API running on http://localhost:{port}")
    print(f"[*] Debug mode: {debug}")
    print(f"[*] API docs: http://localhost:{port}/api")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
