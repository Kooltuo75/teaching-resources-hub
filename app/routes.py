"""
Web routes for the Teaching Resources application.

All routes now use the service layer for data access and business logic,
following enterprise-grade separation of concerns principles.
"""
from flask import Blueprint, render_template, current_app, jsonify, redirect, url_for, abort
import logging

from app.services.resource_service import ResourceService
from app.services.stats_service import StatsService

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


@bp.route('/')
def index():
    """
    Home page - Ultimate Teacher Resource Directory.

    Displays hero section, statistics, featured resources, and category navigation.
    """
    logger.info("Homepage accessed")

    try:
        # Get all categories from service
        categories = ResourceService.get_all_categories()

        # Calculate homepage statistics
        stats = StatsService.calculate_homepage_stats(categories)

        # Get featured resources
        featured_categories = [
            'Educational Websites & Portals',
            'Assessment & Testing Tools',
            'Learning Management Systems',
            'Mathematics Resources',
            'Computer Science & Coding',
            'Video & Multimedia Creation'
        ]
        featured_resources = ResourceService.get_featured_resources(featured_categories, count=6)

        # Get category summary for quick navigation
        category_summary = StatsService.get_category_summary(categories, limit=12)

        return render_template('index.html',
                             app_name=current_app.config['APP_NAME'],
                             stats=stats,
                             featured_resources=featured_resources,
                             categories=category_summary)

    except Exception as e:
        logger.error(f"Error loading homepage: {e}", exc_info=True)
        abort(500)


@bp.route('/about')
def about():
    """About page with project information and mission statement."""
    logger.info("About page accessed")

    # Get statistics for dynamic resource counts
    categories = ResourceService.get_all_categories()
    stats = StatsService.calculate_homepage_stats(categories)

    return render_template('about.html',
                         app_name=current_app.config['APP_NAME'],
                         stats=stats,
                         total_categories=len(categories))


@bp.route('/api-docs')
def api_docs():
    """API documentation page for developers."""
    logger.info("API documentation page accessed")

    return render_template('api_docs.html',
                         app_name=current_app.config['APP_NAME'])


@bp.route('/resources')
def resources():
    """
    Teaching resources directory with searchable categories.

    Displays all 519 resources across 55 categories with advanced filtering.
    """
    logger.info("Resources page accessed")

    try:
        # Get all categories from service
        categories = ResourceService.get_all_categories()

        # Calculate total resources
        total_resources = sum(len(cat.get('resources', [])) for cat in categories)

        logger.debug(f"Loaded {total_resources} resources across {len(categories)} categories")

        return render_template('resources.html',
                             app_name=current_app.config['APP_NAME'],
                             categories=categories,
                             total_resources=total_resources)

    except Exception as e:
        logger.error(f"Error loading resources page: {e}", exc_info=True)
        abort(500)


@bp.route('/category/<category_name>')
def category_detail(category_name):
    """
    Detail page for a specific category.

    Shows category statistics, grade distribution, all resources,
    and related categories.

    Args:
        category_name: Name of the category to display

    Returns:
        Rendered category detail page or redirect if not found
    """
    logger.info(f"Category detail accessed: {category_name}")

    try:
        # Validate category name
        if not ResourceService.validate_category_name(category_name):
            logger.warning(f"Invalid or non-existent category: {category_name}")
            return redirect(url_for('main.resources'))

        # Get category and all categories
        current_category = ResourceService.get_category_by_name(category_name)
        all_categories = ResourceService.get_all_categories()

        if not current_category:
            logger.warning(f"Category not found after validation: {category_name}")
            return redirect(url_for('main.resources'))

        # Calculate category statistics
        resources = current_category.get('resources', [])
        stats = StatsService.calculate_category_stats(resources)

        # Find related categories
        related_categories = StatsService.get_related_categories(
            all_categories,
            current_category,
            count=4
        )

        logger.debug(f"Category {category_name}: {stats['total']} resources, {len(related_categories)} related")

        return render_template('category_detail.html',
                             app_name=current_app.config['APP_NAME'],
                             category=current_category,
                             stats=stats,
                             related_categories=related_categories,
                             total_categories=len(all_categories))

    except Exception as e:
        logger.error(f"Error loading category {category_name}: {e}", exc_info=True)
        abort(500)


@bp.route('/api/resources')
def api_resources():
    """
    API endpoint to get all resources as JSON for autocomplete.

    Returns:
        JSON response with flattened resources array
    """
    logger.debug("API resources endpoint accessed")

    try:
        # Get flattened resources from service
        all_resources = ResourceService.get_all_resources_flat()

        logger.debug(f"API returning {len(all_resources)} resources")

        return jsonify({'resources': all_resources})

    except Exception as e:
        logger.error(f"Error in API resources endpoint: {e}", exc_info=True)
        return jsonify({'resources': [], 'error': 'Failed to load resources'}), 500


@bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        JSON response with status and resource count
    """
    try:
        # Check if we can load resources
        categories = ResourceService.get_all_categories()
        total_resources = sum(len(cat.get('resources', [])) for cat in categories)

        return jsonify({
            'status': 'healthy',
            'app_name': current_app.config['APP_NAME'],
            'categories': len(categories),
            'resources': total_resources
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


# Register authentication routes
from app.auth_routes import register_auth_routes
register_auth_routes(bp)

# Register favorites routes
from app.favorites_routes import register_favorites_routes
register_favorites_routes(bp)

# Register profile routes
from app.profile_routes import register_profile_routes
register_profile_routes(bp)

# Register API routes
from app.api_routes import register_api_routes
register_api_routes(bp)

# Register Google Classroom routes
from app.google_classroom_routes import register_google_classroom_routes
register_google_classroom_routes(bp)

# Register review routes
from app.review_routes import register_review_routes
register_review_routes(bp)

# Register resource submission routes
from app.submission_routes import register_submission_routes
register_submission_routes(bp)

# Register social feature routes
from app.social_routes import register_social_routes
register_social_routes(bp)
