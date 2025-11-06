"""
Favorites/bookmarks routes for managing user's saved resources.
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Favorite
from app.services.resource_service import ResourceService
import logging

logger = logging.getLogger(__name__)


def register_favorites_routes(bp):
    """Register favorites routes to the blueprint."""

    @bp.route('/favorites')
    @login_required
    def favorites():
        """Display user's favorited resources."""
        try:
            # Get all favorites for current user
            user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.created_at.desc()).all()

            # Get full resource details for each favorite
            all_resources = ResourceService.get_all_resources_flat()

            # Create dict for quick resource lookup
            resources_dict = {r['name']: r for r in all_resources}

            # Build list of favorited resources with user notes
            favorited_resources = []
            for fav in user_favorites:
                if fav.resource_name in resources_dict:
                    resource = resources_dict[fav.resource_name].copy()
                    resource['user_note'] = fav.personal_note
                    resource['favorited_at'] = fav.created_at
                    favorited_resources.append(resource)

            # Group by category
            by_category = {}
            for resource in favorited_resources:
                category = resource['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(resource)

            return render_template(
                'favorites.html',
                favorites=favorited_resources,
                by_category=by_category,
                total_count=len(favorited_resources)
            )
        except Exception as e:
            logger.error(f"Error loading favorites: {e}", exc_info=True)
            # Return empty favorites page instead of crashing
            return render_template(
                'favorites.html',
                favorites=[],
                by_category={},
                total_count=0,
                error_message='Unable to load favorites at this time. Please try again later.'
            )

    @bp.route('/api/favorite/add', methods=['POST'])
    @login_required
    def add_favorite():
        """Add a resource to user's favorites."""
        try:
            data = request.get_json()
            resource_name = data.get('resource_name') or data.get('resource_id')  # Support both for backwards compatibility
            resource_category = data.get('resource_category', '')
            resource_url = data.get('resource_url', '')
            notes = data.get('notes', '')

            if not resource_name:
                return jsonify({'success': False, 'message': 'Resource name required'}), 400

            # Check if already favorited
            existing = Favorite.query.filter_by(
                user_id=current_user.id,
                resource_name=resource_name
            ).first()

            if existing:
                return jsonify({'success': False, 'message': 'Already in favorites'}), 400

            # Create favorite
            favorite = Favorite(
                user_id=current_user.id,
                resource_name=resource_name,
                resource_category=resource_category,
                resource_url=resource_url,
                personal_note=notes
            )

            db.session.add(favorite)
            db.session.commit()

            logger.info(f'User {current_user.username} favorited resource {resource_name}')

            return jsonify({
                'success': True,
                'message': 'Added to favorites!'
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding favorite: {e}", exc_info=True)
            return jsonify({'success': False, 'message': 'Failed to add favorite'}), 500

    @bp.route('/api/favorite/remove', methods=['POST'])
    @login_required
    def remove_favorite():
        """Remove a resource from user's favorites."""
        try:
            data = request.get_json()
            resource_name = data.get('resource_name') or data.get('resource_id')  # Support both for backwards compatibility

            if not resource_name:
                return jsonify({'success': False, 'message': 'Resource name required'}), 400

            # Find and delete favorite
            favorite = Favorite.query.filter_by(
                user_id=current_user.id,
                resource_name=resource_name
            ).first()

            if not favorite:
                return jsonify({'success': False, 'message': 'Not in favorites'}), 404

            db.session.delete(favorite)
            db.session.commit()

            logger.info(f'User {current_user.username} removed favorite {resource_name}')

            return jsonify({
                'success': True,
                'message': 'Removed from favorites'
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing favorite: {e}", exc_info=True)
            return jsonify({'success': False, 'message': 'Failed to remove favorite'}), 500

    @bp.route('/api/favorite/update-note', methods=['POST'])
    @login_required
    def update_favorite_note():
        """Update notes for a favorited resource."""
        try:
            data = request.get_json()
            resource_name = data.get('resource_name') or data.get('resource_id')  # Support both for backwards compatibility
            notes = data.get('notes', '')

            if not resource_name:
                return jsonify({'success': False, 'message': 'Resource name required'}), 400

            # Find favorite
            favorite = Favorite.query.filter_by(
                user_id=current_user.id,
                resource_name=resource_name
            ).first()

            if not favorite:
                return jsonify({'success': False, 'message': 'Not in favorites'}), 404

            favorite.personal_note = notes
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Note updated'
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating favorite note: {e}", exc_info=True)
            return jsonify({'success': False, 'message': 'Failed to update note'}), 500

    @bp.route('/api/favorites/check', methods=['POST'])
    @login_required
    def check_favorites():
        """Check which resources are favorited by the current user."""
        try:
            data = request.get_json()
            resource_names = data.get('resource_names', data.get('resource_ids', []))  # Support both for backwards compatibility

            if not resource_names:
                return jsonify({'favorited': {}})

            # Get all favorites for these resources
            favorites = Favorite.query.filter(
                Favorite.user_id == current_user.id,
                Favorite.resource_name.in_(resource_names)
            ).all()

            favorited = {fav.resource_name: True for fav in favorites}

            return jsonify({'favorited': favorited})
        except Exception as e:
            logger.error(f"Error checking favorites: {e}", exc_info=True)
            return jsonify({'favorited': {}})
