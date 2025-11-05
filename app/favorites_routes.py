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
        # Get all favorites for current user
        user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.added_at.desc()).all()

        # Get full resource details for each favorite
        resource_service = ResourceService()
        all_resources = resource_service.get_all_resources()

        # Create dict for quick resource lookup
        resources_dict = {r['id']: r for r in all_resources}

        # Build list of favorited resources with user notes
        favorited_resources = []
        for fav in user_favorites:
            if fav.resource_id in resources_dict:
                resource = resources_dict[fav.resource_id].copy()
                resource['user_note'] = fav.notes
                resource['favorited_at'] = fav.added_at
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

    @bp.route('/api/favorite/add', methods=['POST'])
    @login_required
    def add_favorite():
        """Add a resource to user's favorites."""
        data = request.get_json()
        resource_id = data.get('resource_id')
        notes = data.get('notes', '')

        if not resource_id:
            return jsonify({'success': False, 'message': 'Resource ID required'}), 400

        # Check if already favorited
        existing = Favorite.query.filter_by(
            user_id=current_user.id,
            resource_id=resource_id
        ).first()

        if existing:
            return jsonify({'success': False, 'message': 'Already in favorites'}), 400

        # Create favorite
        favorite = Favorite(
            user_id=current_user.id,
            resource_id=resource_id,
            notes=notes
        )

        db.session.add(favorite)
        db.session.commit()

        logger.info(f'User {current_user.username} favorited resource {resource_id}')

        return jsonify({
            'success': True,
            'message': 'Added to favorites!'
        })

    @bp.route('/api/favorite/remove', methods=['POST'])
    @login_required
    def remove_favorite():
        """Remove a resource from user's favorites."""
        data = request.get_json()
        resource_id = data.get('resource_id')

        if not resource_id:
            return jsonify({'success': False, 'message': 'Resource ID required'}), 400

        # Find and delete favorite
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            resource_id=resource_id
        ).first()

        if not favorite:
            return jsonify({'success': False, 'message': 'Not in favorites'}), 404

        db.session.delete(favorite)
        db.session.commit()

        logger.info(f'User {current_user.username} removed favorite {resource_id}')

        return jsonify({
            'success': True,
            'message': 'Removed from favorites'
        })

    @bp.route('/api/favorite/update-note', methods=['POST'])
    @login_required
    def update_favorite_note():
        """Update notes for a favorited resource."""
        data = request.get_json()
        resource_id = data.get('resource_id')
        notes = data.get('notes', '')

        if not resource_id:
            return jsonify({'success': False, 'message': 'Resource ID required'}), 400

        # Find favorite
        favorite = Favorite.query.filter_by(
            user_id=current_user.id,
            resource_id=resource_id
        ).first()

        if not favorite:
            return jsonify({'success': False, 'message': 'Not in favorites'}), 404

        favorite.notes = notes
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Note updated'
        })

    @bp.route('/api/favorites/check', methods=['POST'])
    @login_required
    def check_favorites():
        """Check which resources are favorited by the current user."""
        data = request.get_json()
        resource_ids = data.get('resource_ids', [])

        if not resource_ids:
            return jsonify({'favorited': {}})

        # Get all favorites for these resources
        favorites = Favorite.query.filter(
            Favorite.user_id == current_user.id,
            Favorite.resource_id.in_(resource_ids)
        ).all()

        favorited = {fav.resource_id: True for fav in favorites}

        return jsonify({'favorited': favorited})
