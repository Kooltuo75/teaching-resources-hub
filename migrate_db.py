"""
Database migration script for Teacher Room enhancements.
Phase 1: Adds the twitter_handle column
Phase 2: Adds Collaboration Board columns (looking_for, can_help_with, open_to_collaboration)
"""
from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Running database migrations...")

    # Check if twitter_handle column exists
    try:
        with db.engine.connect() as conn:
            # Try to query the column
            result = conn.execute(text("SELECT twitter_handle FROM users LIMIT 1"))
            print("[INFO] twitter_handle column already exists")
    except Exception as e:
        # Column doesn't exist, add it
        print("[INFO] Adding twitter_handle column to users table...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN twitter_handle VARCHAR(50)"))
                conn.commit()
            print("[OK] twitter_handle column added successfully!")
        except Exception as migration_error:
            print(f"[ERROR] Failed to add column: {migration_error}")
            raise

    # Phase 2: Check if Collaboration Board columns exist

    # Check looking_for column
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT looking_for FROM users LIMIT 1"))
            print("[INFO] looking_for column already exists")
    except Exception as e:
        print("[INFO] Adding looking_for column to users table...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN looking_for TEXT"))
                conn.commit()
            print("[OK] looking_for column added successfully!")
        except Exception as migration_error:
            print(f"[ERROR] Failed to add column: {migration_error}")
            raise

    # Check can_help_with column
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT can_help_with FROM users LIMIT 1"))
            print("[INFO] can_help_with column already exists")
    except Exception as e:
        print("[INFO] Adding can_help_with column to users table...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN can_help_with TEXT"))
                conn.commit()
            print("[OK] can_help_with column added successfully!")
        except Exception as migration_error:
            print(f"[ERROR] Failed to add column: {migration_error}")
            raise

    # Check open_to_collaboration column
    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT open_to_collaboration FROM users LIMIT 1"))
            print("[INFO] open_to_collaboration column already exists")
    except Exception as e:
        print("[INFO] Adding open_to_collaboration column to users table...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN open_to_collaboration BOOLEAN DEFAULT 1"))
                conn.commit()
            print("[OK] open_to_collaboration column added successfully!")
        except Exception as migration_error:
            print(f"[ERROR] Failed to add column: {migration_error}")
            raise

    print("\n[SUCCESS] Database migration completed!")
