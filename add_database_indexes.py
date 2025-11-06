"""
Add database indexes for performance optimization.

This script adds indexes to frequently queried columns to speed up database queries.
Run this after deploying the app to production.
"""

from app import create_app
from app.models import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_indexes():
    """Add database indexes for performance optimization."""
    app = create_app()

    with app.app_context():
        logger.info("Adding database indexes for performance...")

        try:
            # Add indexes using raw SQL (more reliable than ALTER TABLE)
            indexes = [
                # User table indexes
                ("idx_user_username", "CREATE INDEX IF NOT EXISTS idx_user_username ON users(username)"),
                ("idx_user_email", "CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)"),
                ("idx_user_reputation", "CREATE INDEX IF NOT EXISTS idx_user_reputation ON users(reputation_score DESC)"),

                # Review table indexes
                ("idx_review_resource", "CREATE INDEX IF NOT EXISTS idx_review_resource ON reviews(resource_name)"),
                ("idx_review_user", "CREATE INDEX IF NOT EXISTS idx_review_user ON reviews(user_id)"),
                ("idx_review_created", "CREATE INDEX IF NOT EXISTS idx_review_created ON reviews(created_at DESC)"),
                ("idx_review_rating", "CREATE INDEX IF NOT EXISTS idx_review_rating ON reviews(rating)"),

                # ResourceSubmission table indexes
                ("idx_submission_user", "CREATE INDEX IF NOT EXISTS idx_submission_user ON resource_submissions(user_id)"),
                ("idx_submission_status", "CREATE INDEX IF NOT EXISTS idx_submission_status ON resource_submissions(status)"),
                ("idx_submission_created", "CREATE INDEX IF NOT EXISTS idx_submission_created ON resource_submissions(created_at DESC)"),

                # Follow table indexes
                ("idx_follow_follower", "CREATE INDEX IF NOT EXISTS idx_follow_follower ON follows(follower_id)"),
                ("idx_follow_followed", "CREATE INDEX IF NOT EXISTS idx_follow_followed ON follows(followed_id)"),

                # Activity table indexes
                ("idx_activity_user", "CREATE INDEX IF NOT EXISTS idx_activity_user ON activities(user_id)"),
                ("idx_activity_created", "CREATE INDEX IF NOT EXISTS idx_activity_created ON activities(created_at DESC)"),
                ("idx_activity_type", "CREATE INDEX IF NOT EXISTS idx_activity_type ON activities(activity_type)"),

                # Favorites table indexes
                ("idx_favorite_user", "CREATE INDEX IF NOT EXISTS idx_favorite_user ON favorites(user_id)"),
                ("idx_favorite_resource", "CREATE INDEX IF NOT EXISTS idx_favorite_resource ON favorites(resource_name)"),

                # ReviewHelpful table indexes
                ("idx_review_helpful_user", "CREATE INDEX IF NOT EXISTS idx_review_helpful_user ON review_helpful(user_id)"),
                ("idx_review_helpful_review", "CREATE INDEX IF NOT EXISTS idx_review_helpful_review ON review_helpful(review_id)"),
            ]

            for index_name, sql in indexes:
                try:
                    db.session.execute(db.text(sql))
                    logger.info(f"✓ Created index: {index_name}")
                except Exception as e:
                    logger.warning(f"✗ Index {index_name} might already exist: {e}")

            db.session.commit()
            logger.info("✓ Database indexes added successfully!")
            logger.info(f"✓ Total indexes created/verified: {len(indexes)}")

        except Exception as e:
            logger.error(f"✗ Error adding indexes: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    add_indexes()
