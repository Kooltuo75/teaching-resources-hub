"""
Performance middleware for static file caching and optimization.
"""

from flask import make_response, request
from functools import wraps


def configure_caching(app):
    """
    Configure caching headers for static files and responses.

    Args:
        app: Flask application instance
    """

    @app.after_request
    def add_cache_headers(response):
        """Add caching headers to static files."""
        # Only cache GET requests
        if request.method != 'GET':
            return response

        # Cache static files for 1 year
        if '/static/' in request.path:
            response.cache_control.max_age = 31536000  # 1 year
            response.cache_control.public = True

        # Cache CSS and JS files
        elif request.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot')):
            response.cache_control.max_age = 31536000  # 1 year
            response.cache_control.public = True

        # Cache HTML pages for 5 minutes (with must-revalidate)
        elif response.content_type and 'text/html' in response.content_type:
            response.cache_control.max_age = 300  # 5 minutes
            response.cache_control.must_revalidate = True

        # Cache JSON API responses for 1 minute
        elif response.content_type and 'application/json' in response.content_type:
            response.cache_control.max_age = 60  # 1 minute
            response.cache_control.public = True

        return response

    app.logger.info("Static file caching configured")


def cache_for(seconds=300):
    """
    Decorator to cache a view for a specified number of seconds.

    Args:
        seconds: Number of seconds to cache the response

    Example:
        @app.route('/expensive')
        @cache_for(600)  # Cache for 10 minutes
        def expensive_view():
            return expensive_computation()
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            response.cache_control.max_age = seconds
            response.cache_control.public = True
            return response
        return decorated_function
    return decorator
