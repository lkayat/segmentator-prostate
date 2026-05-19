#!/usr/bin/env python3
"""
Runner script for the web-based prostate MRI segmentation GUI
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main function to run the web interface"""
    print("Starting Prostate MRI Segmentation Web Interface...")
    print("=" * 60)
    print("This is a web-based interface that runs in a browser")
    print("To access the application, open your browser and go to:")
    print("http://localhost:5000")
    print("=" * 60)

    # Import and run the web application
    try:
        from web_gui import app, socketio

        # Create default user if none exists
        from web_gui import db, User
        with app.app_context():
            if not User.query.first():
                print("Creating default admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@prostate-segmentation.org',
                    password_hash='admin',
                    role='admin'
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin user created (username: admin, password: admin)")

        print("\nStarting web server on http://localhost:5000")
        print("Press Ctrl+C to stop the server")

        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)

    except Exception as e:
        print(f"Error starting web interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()