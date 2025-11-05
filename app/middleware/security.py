"""
Security Middleware - Adds enterprise-grade security headers.

This middleware implements security best practices including:
- Content Security Policy
- XSS Protection
- Clickjacking Protection
- MIME Sniffing Protection
- HTTPS Enforcement
"""

from flask import Flask


def add_security_headers(app: Flask):
    """
    Add security headers to all responses.

    Implements OWASP security best practices for web applications.

    Args:
        app: Flask application instance
    """

    @app.after_request
    def set_security_headers(response):
        """Add security headers to every response."""

        # Content Security Policy - Prevents XSS and other injection attacks
        # Allow resources from same origin, inline styles/scripts for our app to work
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "  # Allow inline scripts for our JS
            "style-src 'self' 'unsafe-inline'; "   # Allow inline styles for our CSS
            "img-src 'self' data: https:; "        # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:; "              # Allow fonts
            "connect-src 'self'; "                 # Allow API calls to same origin
            "frame-ancestors 'none'; "             # Prevent framing (same as X-Frame-Options)
            "base-uri 'self'; "                    # Prevent base tag hijacking
            "form-action 'self'"                   # Only allow forms to submit to same origin
        )

        # X-Frame-Options - Prevents clickjacking attacks
        response.headers['X-Frame-Options'] = 'DENY'

        # X-Content-Type-Options - Prevents MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # X-XSS-Protection - Legacy XSS protection (for older browsers)
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Strict-Transport-Security - Enforces HTTPS (only in production)
        # Note: Only set this if you're using HTTPS
        if not app.debug:
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains'
            )

        # Referrer-Policy - Controls referrer information
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions-Policy - Controls browser features
        response.headers['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=()'
        )

        return response


def configure_security(app: Flask):
    """
    Configure all security settings for the application.

    Args:
        app: Flask application instance
    """
    # Add security headers
    add_security_headers(app)

    # Set secure session cookie settings
    app.config['SESSION_COOKIE_SECURE'] = not app.debug  # Only send over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

    # Permanent session lifetime (30 days)
    app.config['PERMANENT_SESSION_LIFETIME'] = 2592000
