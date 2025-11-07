"""
Create an admin account for the Teaching Resources Hub.
Run this script once to create your admin user.
"""
from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import text
import subprocess
import sys

print("[INFO] Running database migrations first...")
try:
    result = subprocess.run([sys.executable, 'migrate_db.py'],
                          capture_output=True,
                          text=True,
                          timeout=60)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print("[WARNING] Migration had some issues, but continuing...")
except Exception as e:
    print(f"[WARNING] Could not run migration: {e}")
    print("[INFO] Continuing anyway...")

app = create_app()

with app.app_context():
    # Admin credentials
    admin_username = "admin"
    admin_email = "admin@teachinghub.com"
    admin_password = "Admin123!"

    # Check if admin already exists
    existing_admin = User.query.filter_by(username=admin_username).first()

    if existing_admin:
        print(f"[INFO] User '{admin_username}' already exists. Updating to admin...")
        if hasattr(existing_admin, 'is_admin'):
            existing_admin.is_admin = True
        if hasattr(existing_admin, 'is_moderator'):
            existing_admin.is_moderator = True
        if hasattr(existing_admin, 'is_verified_teacher'):
            existing_admin.is_verified_teacher = True
        db.session.commit()
        print(f"[SUCCESS] User '{admin_username}' is now an admin!")
    else:
        print(f"[INFO] Creating new admin user '{admin_username}'...")

        # Create new admin user with basic fields
        admin_data = {
            'username': admin_username,
            'email': admin_email,
            'password': generate_password_hash(admin_password),
            'display_name': "Administrator",
            'profile_public': True,
            'bio': "System Administrator",
            'grade_level': "All Grades",
            'subjects_taught': "Administration"
        }

        # Add optional fields if they exist in the model
        if hasattr(User, 'is_admin'):
            admin_data['is_admin'] = True
        if hasattr(User, 'is_moderator'):
            admin_data['is_moderator'] = True
        if hasattr(User, 'is_verified_teacher'):
            admin_data['is_verified_teacher'] = True

        admin_user = User(**admin_data)

        db.session.add(admin_user)
        db.session.commit()

        print("[SUCCESS] Admin account created!")

    print("\n" + "="*50)
    print("ADMIN LOGIN CREDENTIALS")
    print("="*50)
    print(f"Username: {admin_username}")
    print(f"Email:    {admin_email}")
    print(f"Password: {admin_password}")
    print("="*50)
    print("\nPlease login at: /login")
    print("Admin dashboard at: /admin")
    print("\n⚠️  IMPORTANT: Change the password after first login!")
