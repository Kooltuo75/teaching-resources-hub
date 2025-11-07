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
                conn.execute(text("ALTER TABLE users ADD COLUMN open_to_collaboration BOOLEAN DEFAULT TRUE"))
                conn.commit()
            print("[OK] open_to_collaboration column added successfully!")
        except Exception as migration_error:
            print(f"[ERROR] Failed to add column: {migration_error}")
            raise

    # Phase 2: What I'm Teaching Now columns

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT current_unit_title FROM users LIMIT 1"))
            print("[INFO] current_unit_title column already exists")
    except Exception as e:
        print("[INFO] Adding current_unit_title column...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN current_unit_title VARCHAR(200)"))
                conn.commit()
            print("[OK] current_unit_title added!")
        except Exception as err:
            print(f"[ERROR] {err}")
            raise

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT current_unit_subject FROM users LIMIT 1"))
            print("[INFO] current_unit_subject column already exists")
    except Exception as e:
        print("[INFO] Adding current_unit_subject column...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN current_unit_subject VARCHAR(100)"))
                conn.commit()
            print("[OK] current_unit_subject added!")
        except Exception as err:
            print(f"[ERROR] {err}")
            raise

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT current_unit_description FROM users LIMIT 1"))
            print("[INFO] current_unit_description column already exists")
    except Exception as e:
        print("[INFO] Adding current_unit_description column...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN current_unit_description TEXT"))
                conn.commit()
            print("[OK] current_unit_description added!")
        except Exception as err:
            print(f"[ERROR] {err}")
            raise

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT current_unit_updated FROM users LIMIT 1"))
            print("[INFO] current_unit_updated column already exists")
    except Exception as e:
        print("[INFO] Adding current_unit_updated column...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN current_unit_updated TIMESTAMP"))
                conn.commit()
            print("[OK] current_unit_updated added!")
        except Exception as err:
            print(f"[ERROR] {err}")
            raise

    # Phase 2: Professional Achievements column

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT achievements FROM users LIMIT 1"))
            print("[INFO] achievements column already exists")
    except Exception as e:
        print("[INFO] Adding achievements column...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN achievements TEXT"))
                conn.commit()
            print("[OK] achievements added!")
        except Exception as err:
            print(f"[ERROR] {err}")
            raise

    # Phase 2: Create new tables (Teaching Journey, Classroom Photos, Favorite Lessons)

    print("\n[INFO] Creating Phase 2 tables if they don't exist...")
    try:
        # This will create all missing tables defined in models.py
        db.create_all()
        print("[OK] All Phase 2 tables created or already exist!")
    except Exception as e:
        print(f"[ERROR] Failed to create tables: {e}")
        raise

    # Phase 3: Admin system columns

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT is_admin FROM users LIMIT 1"))
            print("[INFO] is_admin column already exists")
    except Exception as e:
        print("[INFO] Adding is_admin column...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("[OK] is_admin added!")
        except Exception as err:
            print(f"[ERROR] {err}")
            raise

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT is_banned FROM users LIMIT 1"))
            print("[INFO] is_banned column already exists")
    except Exception as e:
        print("[INFO] Adding is_banned column...")
        try:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE"))
                conn.commit()
            print("[OK] is_banned added!")
        except Exception as err:
            print(f"[ERROR] {err}")
            raise

    print("\n[SUCCESS] Database migration completed!")
