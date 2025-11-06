"""
Profile routes for user profile pages and customization.
MySpace-style customizable teacher "Room" feature.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, User, Favorite, ProfileVisit
from app.services.resource_service import ResourceService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register_profile_routes(bp):
    """Register profile routes to the blueprint."""

    @bp.route('/profile/<username>')
    def profile(username):
        """Display a user's public profile 'Room'."""
        # Get the profile owner
        user = User.query.filter_by(username=username).first()

        if not user:
            flash(f'User {username} not found.', 'error')
            return redirect(url_for('main.index'))

        # Record profile visit if not viewing own profile
        try:
            if current_user.is_authenticated and current_user.id != user.id:
                visit = ProfileVisit(
                    profile_id=user.id,
                    visitor_id=current_user.id
                )
                db.session.add(visit)
                db.session.commit()
            elif not current_user.is_authenticated:
                # Record anonymous visit
                visit = ProfileVisit(profile_id=user.id)
                db.session.add(visit)
                db.session.commit()
        except Exception as e:
            logger.debug(f"Could not record profile visit: {e}")
            db.session.rollback()

        # Get user's favorites
        try:
            user_favorites = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.added_at.desc()).limit(12).all()
        except Exception as e:
            logger.debug(f"Could not load favorites: {e}")
            user_favorites = []

        # Get full resource details for favorites
        all_resources = ResourceService.get_all_resources_flat()
        resources_dict = {r['name']: r for r in all_resources}

        favorited_resources = []
        for fav in user_favorites:
            if fav.resource_name in resources_dict:
                resource = resources_dict[fav.resource_name].copy()
                favorited_resources.append(resource)

        # Get profile statistics
        try:
            total_favorites = Favorite.query.filter_by(user_id=user.id).count()
            total_visits = ProfileVisit.query.filter_by(profile_id=user.id).count()
        except Exception as e:
            logger.debug(f"Could not load profile stats: {e}")
            total_favorites = 0
            total_visits = 0

        # Get recent visitors (excluding owner)
        try:
            recent_visitors = ProfileVisit.query.filter(
                ProfileVisit.profile_id == user.id,
                ProfileVisit.visitor_id.isnot(None),
                ProfileVisit.visitor_id != user.id
            ).order_by(ProfileVisit.visited_at.desc()).limit(5).all()

            visitor_users = []
            for visit in recent_visitors:
                visitor = User.query.get(visit.visitor_id)
                if visitor:
                    visitor_users.append(visitor)
        except Exception as e:
            logger.debug(f"Could not load recent visitors: {e}")
            visitor_users = []

        is_own_profile = current_user.is_authenticated and current_user.id == user.id

        return render_template(
            'profile/profile.html',
            profile_user=user,
            is_own_profile=is_own_profile,
            favorites=favorited_resources,
            total_favorites=total_favorites,
            total_visits=total_visits,
            recent_visitors=visitor_users
        )

    @bp.route('/profile/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        """Edit user's profile customization."""
        if request.method == 'POST':
            # Update basic info
            current_user.display_name = request.form.get('display_name', '').strip() or current_user.username
            current_user.bio = request.form.get('bio', '').strip()
            current_user.teaching_philosophy = request.form.get('teaching_philosophy', '').strip()
            current_user.school = request.form.get('school', '').strip()
            current_user.grade_levels = request.form.get('grade_levels', '').strip()
            current_user.subjects = request.form.get('subjects', '').strip()

            # Update customization
            current_user.background_color = request.form.get('background_color', '#ffffff')
            current_user.text_color = request.form.get('text_color', '#333333')
            current_user.accent_color = request.form.get('accent_color', '#667eea')
            current_user.profile_theme = request.form.get('profile_theme', 'light')

            # Update URLs
            current_user.website_url = request.form.get('website_url', '').strip()
            current_user.twitter_handle = request.form.get('twitter_handle', '').strip()

            db.session.commit()

            logger.info(f'User {current_user.username} updated their profile')
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile', username=current_user.username))

        return render_template('profile/edit_profile.html')

    @bp.route('/api/profile/theme-preview', methods=['POST'])
    @login_required
    def theme_preview():
        """Return theme preview data (for live preview in edit page)."""
        from flask import jsonify

        data = request.get_json()
        return jsonify({
            'success': True,
            'theme': {
                'background_color': data.get('background_color', '#ffffff'),
                'text_color': data.get('text_color', '#333333'),
                'accent_color': data.get('accent_color', '#667eea'),
                'profile_theme': data.get('profile_theme', 'light')
            }
        })
