"""
Database migration script for Phase 1 Teacher Room enhancements.
Adds the twitter_handle column to the users table.
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

    print("\n[SUCCESS] Database migration completed!")
