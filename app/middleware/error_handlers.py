"""
Error Handlers - Custom error pages for production-ready application.

Provides user-friendly error pages instead of default Flask pages.
"""

import logging
from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask):
    """
    Register custom error handlers for the application.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        logger.warning(f"404 error: {error}")
        return render_template('errors/404.html',
                             app_name=app.config.get('APP_NAME', 'Teaching Resources Hub')), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        logger.error(f"500 error: {error}", exc_info=True)
        return render_template('errors/500.html',
                             app_name=app.config.get('APP_NAME', 'Teaching Resources Hub')), 500

    @app.errorhandler(503)
    def service_unavailable_error(error):
        """Handle 503 Service Unavailable errors."""
        logger.error(f"503 error: {error}")
        return render_template('errors/503.html',
                             app_name=app.config.get('APP_NAME', 'Teaching Resources Hub')), 503

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors."""
        logger.error(f"Unexpected error: {error}", exc_info=True)

        # If it's an HTTP exception, use its code
        if isinstance(error, HTTPException):
            return render_template('errors/500.html',
                                 app_name=app.config.get('APP_NAME', 'Teaching Resources Hub')), error.code

        # For other exceptions, return 500
        return render_template('errors/500.html',
                             app_name=app.config.get('APP_NAME', 'Teaching Resources Hub')), 500
