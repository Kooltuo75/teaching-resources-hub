"""
Analytics Dashboard Routes
"""

from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from app.services.analytics_service import AnalyticsService
import logging

bp = Blueprint('analytics', __name__, url_prefix='/analytics')
logger = logging.getLogger(__name__)


def admin_required(f):
    """Decorator to require admin access for analytics."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_moderator:
            logger.warning(f"Non-admin user {current_user.username} attempted to access analytics")
            return "Access denied. Admin privileges required.", 403
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Analytics dashboard showing key metrics and insights.

    Requires moderator/admin access.
    """
    logger.info(f"Analytics dashboard accessed by {current_user.username}")

    # Get time period from query params (default 7 days)
    from flask import request
    days = int(request.args.get('days', 7))

    # Get analytics data
    stats = AnalyticsService.get_site_statistics(days=days)
    top_resources = AnalyticsService.get_top_resources(days=days, limit=10)
    top_categories = AnalyticsService.get_top_categories(days=days, limit=10)
    top_searches = AnalyticsService.get_top_searches(days=days, limit=10)
    daily_activity = AnalyticsService.get_daily_activity(days=days)

    return render_template('analytics/dashboard.html',
                         app_name=current_app.config['APP_NAME'],
                         stats=stats,
                         top_resources=top_resources,
                         top_categories=top_categories,
                         top_searches=top_searches,
                         daily_activity=daily_activity,
                         days=days)


@bp.route('/api/stats')
@admin_required
def api_stats():
    """
    API endpoint for analytics statistics.

    Returns JSON data for charts and real-time updates.
    """
    from flask import request
    days = int(request.args.get('days', 7))

    stats = AnalyticsService.get_site_statistics(days=days)

    return jsonify(stats)


@bp.route('/api/top-resources')
@admin_required
def api_top_resources():
    """API endpoint for top resources."""
    from flask import request
    days = int(request.args.get('days', 7))
    limit = int(request.args.get('limit', 10))

    resources = AnalyticsService.get_top_resources(days=days, limit=limit)

    return jsonify(resources)


@bp.route('/api/top-categories')
@admin_required
def api_top_categories():
    """API endpoint for top categories."""
    from flask import request
    days = int(request.args.get('days', 7))
    limit = int(request.args.get('limit', 10))

    categories = AnalyticsService.get_top_categories(days=days, limit=limit)

    return jsonify(categories)


@bp.route('/api/daily-activity')
@admin_required
def api_daily_activity():
    """API endpoint for daily activity chart data."""
    from flask import request
    days = int(request.args.get('days', 7))

    activity = AnalyticsService.get_daily_activity(days=days)

    return jsonify(activity)
