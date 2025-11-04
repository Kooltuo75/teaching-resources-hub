"""
Initialize the Flask application.
"""
from flask import Flask
from config import Config

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register routes
    from app import routes
    app.register_blueprint(routes.bp)

    return app
