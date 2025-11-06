"""
Setup Analytics - Create tables and grant admin access.
"""

from app import create_app
from app.models import db, User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_analytics():
    """Create analytics tables and make testteacher a moderator."""
    app = create_app()

    with app.app_context():
        logger.info("Setting up analytics...")

        # Create all database tables (including new analytics tables)
        logger.info("Creating database tables...")
        db.create_all()
        logger.info("✓ Database tables created/updated")

        # Make testteacher a moderator
        user = User.query.filter_by(username='testteacher').first()
        if user:
            user.is_moderator = True
            db.session.commit()
            logger.info(f"✓ Made '{user.username}' a moderator for analytics access")
        else:
            logger.warning("✗ User 'testteacher' not found")

        logger.info("\n✓ Analytics setup complete!")
        logger.info("\nYou can now access the analytics dashboard at:")
        logger.info("/analytics/dashboard")
        logger.info("\nLogin with: testteacher / password123")

if __name__ == '__main__':
    setup_analytics()
