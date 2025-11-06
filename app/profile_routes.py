"""
Profile routes for user profile pages and customization.
MySpace-style customizable teacher "Room" feature.
"""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import db, User, Favorite, ProfileVisit
from app.services.resource_service import ResourceService
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import logging

logger = logging.getLogger(__name__)

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        # Check privacy settings
        if not user.profile_public and not current_user.is_authenticated:
            flash('This profile is private. Please log in to view it.', 'error')
            return redirect(url_for('main.index'))

        # Check if viewing own profile
        is_own_profile = current_user.is_authenticated and current_user.id == user.id

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

        # Get user's favorites (ALL of them, not just 12!)
        favorited_resources = []
        if user.show_favorites_public or is_own_profile:
            try:
                user_favorites = Favorite.query.filter_by(user_id=user.id).order_by(Favorite.created_at.desc()).all()
            except Exception as e:
                logger.debug(f"Could not load favorites: {e}")
                user_favorites = []

            # Get full resource details for favorites
            all_resources = ResourceService.get_all_resources_flat()
            resources_dict = {r['name']: r for r in all_resources}

            for fav in user_favorites:
                if fav.resource_name in resources_dict:
                    resource = resources_dict[fav.resource_name].copy()
                    resource['personal_note'] = fav.personal_note  # Add user's note
                    resource['favorited_at'] = fav.created_at
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
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename and allowed_file(file.filename):
                    # Check file size
                    file.seek(0, os.SEEK_END)
                    file_length = file.tell()
                    if file_length > MAX_FILE_SIZE:
                        flash('File is too large. Maximum size is 5MB.', 'error')
                        file.seek(0)
                    else:
                        file.seek(0)
                        # Generate unique filename
                        filename = secure_filename(file.filename)
                        unique_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

                        # Save file
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                        os.makedirs(upload_folder, exist_ok=True)
                        file_path = os.path.join(upload_folder, unique_filename)
                        file.save(file_path)

                        # Update database
                        current_user.profile_picture = f'/static/uploads/profiles/{unique_filename}'
                        logger.info(f'User {current_user.username} uploaded profile picture')

            # Update basic info
            current_user.display_name = request.form.get('display_name', '').strip() or current_user.username
            current_user.bio = request.form.get('bio', '').strip()
            current_user.teaching_philosophy = request.form.get('teaching_philosophy', '').strip()
            current_user.school = request.form.get('school', '').strip()
            current_user.grade_level = request.form.get('grade_levels', '').strip()  # Note: form uses grade_levels
            current_user.subjects_taught = request.form.get('subjects', '').strip()  # Note: form uses subjects

            # Phase 1 New Fields
            current_user.favorite_quote = request.form.get('favorite_quote', '').strip()
            current_user.location = request.form.get('location', '').strip()

            # Years teaching (convert to int)
            years_str = request.form.get('years_teaching', '').strip()
            if years_str and years_str.isdigit():
                current_user.years_teaching = int(years_str)
            elif years_str == '':
                current_user.years_teaching = None

            # Privacy settings
            current_user.profile_public = request.form.get('profile_public') == 'on'
            current_user.show_favorites_public = request.form.get('show_favorites_public') == 'on'

            # Update customization
            current_user.background_color = request.form.get('background_color', '#ffffff')
            current_user.text_color = request.form.get('text_color', '#333333')
            current_user.accent_color = request.form.get('accent_color', '#667eea')
            current_user.profile_theme = request.form.get('profile_theme', 'light')

            # Update URLs
            current_user.website = request.form.get('website_url', '').strip()  # Note: model uses 'website'

            # Handle twitter_handle (backward compatible)
            twitter_handle = request.form.get('twitter_handle', '').strip()
            if twitter_handle:
                # Remove @ if user added it
                if twitter_handle.startswith('@'):
                    twitter_handle = twitter_handle[1:]
                # Only set if column exists
                if hasattr(current_user, 'twitter_handle'):
                    current_user.twitter_handle = twitter_handle
                else:
                    logger.warning("twitter_handle column not yet migrated")
            elif hasattr(current_user, 'twitter_handle'):
                # Clear twitter handle if empty
                current_user.twitter_handle = None

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
