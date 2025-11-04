"""
Database migration script to add Google Classroom fields to existing database.
Run this once to update your database schema.
"""

from app import create_app
from app.models import db
import sqlite3

print("[*] Migrating database to add Google Classroom support...")

app = create_app()

with app.app_context():
    # Get database path
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    print(f"[*] Database: {db_path}")

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    migrations_needed = []

    if 'google_id' not in columns:
        migrations_needed.append("ALTER TABLE users ADD COLUMN google_id VARCHAR(100)")

    if 'google_access_token' not in columns:
        migrations_needed.append("ALTER TABLE users ADD COLUMN google_access_token TEXT")

    if 'google_refresh_token' not in columns:
        migrations_needed.append("ALTER TABLE users ADD COLUMN google_refresh_token TEXT")

    if 'google_token_expiry' not in columns:
        migrations_needed.append("ALTER TABLE users ADD COLUMN google_token_expiry DATETIME")

    if 'google_connected' not in columns:
        migrations_needed.append("ALTER TABLE users ADD COLUMN google_connected BOOLEAN DEFAULT 0")

    if not migrations_needed:
        print("[OK] Database is already up to date!")
    else:
        print(f"[*] Applying {len(migrations_needed)} migrations...")

        for migration in migrations_needed:
            print(f"    Executing: {migration}")
            cursor.execute(migration)

        conn.commit()
        print("[OK] Database migration completed successfully!")

    conn.close()

print("\n[OK] Done! Your database is now ready for Google Classroom integration.")
print("\nNext steps:")
print("1. Follow the setup guide in GOOGLE_CLASSROOM_SETUP.md")
print("2. Get your Google OAuth credentials from Google Cloud Console")
print("3. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
print("4. Restart your application: python run.py")
