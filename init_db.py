"""
Initialize the database with all tables.
"""
from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("[OK] Database tables created successfully!")
    print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # List all tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n[INFO] Created {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")
