"""
Analytics Middleware - Automatically track page views and performance.
"""

import time
import logging
from flask import request, g
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


def configure_analytics(app):
    """
    Configure analytics middleware to track all requests.

    Args:
        app: Flask application instance
    """

    @app.before_request
    def before_request():
        """Record request start time."""
        g.start_time = time.time()

    @app.after_request
    def track_request(response):
        """Track page view after request completes."""
        # Calculate response time
        response_time = time.time() - g.get('start_time', time.time())

        # Only track GET requests to avoid tracking form submissions multiple times
        if request.method == 'GET':
            # Skip static files and health checks
            if not request.path.startswith('/static/') and request.path != '/health':
                try:
                    AnalyticsService.track_page_view(
                        path=request.path,
                        method=request.method,
                        status_code=response.status_code,
                        response_time=response_time
                    )
                except Exception as e:
                    # Don't break the request if analytics fails
                    logger.error(f"Analytics tracking error: {e}")

        return response

    app.logger.info("Analytics middleware configured")
