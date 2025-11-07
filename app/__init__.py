"""
Initialize the Flask application with enterprise-grade middleware and error handling.
"""
from flask import Flask
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app(config_class=Config):
    """
    Create and configure the Flask application.

    Implements enterprise-grade patterns:
    - Security headers middleware
    - Custom error handlers
    - Comprehensive logging
    - Service layer architecture
    - User authentication system
    - Database integration

    Args:
        config_class: Configuration class to use

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    from app.models import db, init_db
    init_db(app)

    # Initialize Flask-Compress for response compression
    from flask_compress import Compress
    Compress(app)

    # Initialize Flask-Login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Register Jinja filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks."""
        if not text:
            return ''
        return text.replace('\n', '<br>\n')

    # Configure logging
    configure_logging(app)

    # Register security middleware
    from app.middleware.security import configure_security
    configure_security(app)

    # Register performance middleware (caching)
    from app.middleware.performance import configure_caching
    configure_caching(app)

    # Register analytics middleware
    from app.middleware.analytics_middleware import configure_analytics
    configure_analytics(app)

    # Register error handlers
    from app.middleware.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Register routes blueprint
    from app import routes
    app.register_blueprint(routes.bp)

    # Register analytics routes
    from app import analytics_routes
    app.register_blueprint(analytics_routes.bp)

    app.logger.info('Teaching Resources Hub application started')

    return app


def configure_logging(app):
    """
    Configure comprehensive logging for the application.

    Sets up both file and console logging with appropriate levels.

    Args:
        app: Flask application instance
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # File handler with rotation (10MB max, keep 10 backups)
        file_handler = RotatingFileHandler(
            'logs/teaching_resources.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Teaching Resources Hub startup')
    else:
        # In debug mode, log to console
        app.logger.setLevel(logging.DEBUG)
