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
        try:
            # Get the profile owner
            user = User.query.filter_by(username=username).first()

            if not user:
                flash(f'User {username} not found.', 'error')
                return redirect(url_for('main.index'))
        except Exception as e:
            logger.error(f'Error loading user profile: {e}')
            flash('Error loading profile. Please try again.', 'error')
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

        # Load Phase 2 content
        journey_events = []
        classroom_photos = []
        favorite_lessons = []

        try:
            from app.models import TeachingJourneyEvent, ClassroomPhoto, FavoriteLesson

            # Load timeline events (sorted by year DESC)
            try:
                journey_events = TeachingJourneyEvent.query.filter_by(user_id=user.id).order_by(TeachingJourneyEvent.year.desc()).all()
            except Exception as je:
                logger.warning(f"Could not load journey events: {je}")

            # Load classroom photos (limit to 12)
            try:
                classroom_photos = ClassroomPhoto.query.filter_by(user_id=user.id).order_by(ClassroomPhoto.uploaded_at.desc()).limit(12).all()
            except Exception as pe:
                logger.warning(f"Could not load classroom photos: {pe}")

            # Load favorite lessons (limit to 5, ordered by display_order)
            try:
                favorite_lessons = FavoriteLesson.query.filter_by(user_id=user.id).order_by(FavoriteLesson.display_order).limit(5).all()
            except Exception as le:
                logger.warning(f"Could not load favorite lessons: {le}")

        except Exception as e:
            logger.warning(f"Could not import Phase 2 models: {e}")
            # Continue with empty lists

        return render_template(
            'profile/profile.html',
            profile_user=user,
            is_own_profile=is_own_profile,
            favorites=favorited_resources,
            total_favorites=total_favorites,
            total_visits=total_visits,
            recent_visitors=visitor_users,
            journey_events=journey_events,
            classroom_photos=classroom_photos,
            favorite_lessons=favorite_lessons
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

            # Collaboration Board (Phase 2)
            if hasattr(current_user, 'looking_for'):
                current_user.looking_for = request.form.get('looking_for', '').strip()
            if hasattr(current_user, 'can_help_with'):
                current_user.can_help_with = request.form.get('can_help_with', '').strip()
            if hasattr(current_user, 'open_to_collaboration'):
                current_user.open_to_collaboration = request.form.get('open_to_collaboration') == 'on'

            # What I'm Teaching Now (Phase 2)
            if hasattr(current_user, 'current_unit_title'):
                current_user.current_unit_title = request.form.get('current_unit_title', '').strip()
            if hasattr(current_user, 'current_unit_subject'):
                current_user.current_unit_subject = request.form.get('current_unit_subject', '').strip()
            if hasattr(current_user, 'current_unit_description'):
                desc = request.form.get('current_unit_description', '').strip()
                current_user.current_unit_description = desc
                # Update timestamp if content changed
                if desc and hasattr(current_user, 'current_unit_updated'):
                    from datetime import datetime
                    current_user.current_unit_updated = datetime.utcnow()

            # Professional Achievements (Phase 2)
            if hasattr(current_user, 'achievements'):
                current_user.achievements = request.form.get('achievements', '').strip()

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

    # ========== Teaching Journey Timeline Routes ==========

    @bp.route('/profile/journey/add', methods=['POST'])
    @login_required
    def add_journey_event():
        """Add a new teaching journey timeline event."""
        from flask import jsonify
        from app.models import TeachingJourneyEvent

        try:
            year = int(request.form.get('year', 0))
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            event_type = request.form.get('event_type', '').strip()

            if not year or not title:
                return jsonify({'success': False, 'error': 'Year and title are required'}), 400

            event = TeachingJourneyEvent(
                user_id=current_user.id,
                year=year,
                title=title,
                description=description,
                event_type=event_type
            )
            db.session.add(event)
            db.session.commit()

            logger.info(f'User {current_user.username} added timeline event: {title}')
            return jsonify({'success': True, 'event_id': event.id})

        except Exception as e:
            logger.error(f'Error adding timeline event: {e}')
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/profile/journey/<int:event_id>/delete', methods=['POST'])
    @login_required
    def delete_journey_event(event_id):
        """Delete a teaching journey timeline event."""
        from flask import jsonify
        from app.models import TeachingJourneyEvent

        try:
            event = TeachingJourneyEvent.query.filter_by(id=event_id, user_id=current_user.id).first()
            if not event:
                return jsonify({'success': False, 'error': 'Event not found'}), 404

            db.session.delete(event)
            db.session.commit()

            logger.info(f'User {current_user.username} deleted timeline event {event_id}')
            return jsonify({'success': True})

        except Exception as e:
            logger.error(f'Error deleting timeline event: {e}')
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    # ========== Classroom Photo Gallery Routes ==========

    @bp.route('/profile/photos/upload', methods=['POST'])
    @login_required
    def upload_classroom_photo():
        """Upload a classroom photo."""
        from flask import jsonify
        from app.models import ClassroomPhoto

        try:
            if 'photo' not in request.files:
                return jsonify({'success': False, 'error': 'No photo uploaded'}), 400

            file = request.files['photo']
            if not file or not file.filename:
                return jsonify({'success': False, 'error': 'No photo selected'}), 400

            if not allowed_file(file.filename):
                return jsonify({'success': False, 'error': 'Invalid file type. Please upload an image.'}), 400

            # Check file size
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            if file_length > MAX_FILE_SIZE:
                return jsonify({'success': False, 'error': 'File is too large. Maximum size is 5MB.'}), 400
            file.seek(0)

            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{current_user.id}_classroom_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

            # Save file
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'classroom')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            # Add to database
            caption = request.form.get('caption', '').strip()
            photo_type = request.form.get('photo_type', 'classroom').strip()

            photo = ClassroomPhoto(
                user_id=current_user.id,
                photo_path=f'/static/uploads/classroom/{unique_filename}',
                caption=caption,
                photo_type=photo_type
            )
            db.session.add(photo)
            db.session.commit()

            logger.info(f'User {current_user.username} uploaded classroom photo')
            return jsonify({'success': True, 'photo_id': photo.id, 'photo_url': photo.photo_path})

        except Exception as e:
            logger.error(f'Error uploading photo: {e}')
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/profile/photos/<int:photo_id>/delete', methods=['POST'])
    @login_required
    def delete_classroom_photo(photo_id):
        """Delete a classroom photo."""
        from flask import jsonify
        from app.models import ClassroomPhoto

        try:
            photo = ClassroomPhoto.query.filter_by(id=photo_id, user_id=current_user.id).first()
            if not photo:
                return jsonify({'success': False, 'error': 'Photo not found'}), 404

            # Delete file from filesystem
            try:
                file_path = os.path.join(current_app.root_path, photo.photo_path.lstrip('/'))
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as file_error:
                logger.warning(f'Could not delete photo file: {file_error}')

            db.session.delete(photo)
            db.session.commit()

            logger.info(f'User {current_user.username} deleted classroom photo {photo_id}')
            return jsonify({'success': True})

        except Exception as e:
            logger.error(f'Error deleting photo: {e}')
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    # ========== Favorite Lessons Routes ==========

    @bp.route('/profile/lessons/add', methods=['POST'])
    @login_required
    def add_favorite_lesson():
        """Add a new favorite lesson."""
        from flask import jsonify
        from app.models import FavoriteLesson

        try:
            title = request.form.get('title', '').strip()
            subject = request.form.get('subject', '').strip()
            grade_level = request.form.get('grade_level', '').strip()
            description = request.form.get('description', '').strip()
            materials_needed = request.form.get('materials_needed', '').strip()
            duration = request.form.get('duration', '').strip()
            learning_objectives = request.form.get('learning_objectives', '').strip()

            if not title or not description:
                return jsonify({'success': False, 'error': 'Title and description are required'}), 400

            # Check if user already has 5 lessons (limit)
            lesson_count = FavoriteLesson.query.filter_by(user_id=current_user.id).count()
            if lesson_count >= 5:
                return jsonify({'success': False, 'error': 'Maximum 5 favorite lessons allowed'}), 400

            lesson = FavoriteLesson(
                user_id=current_user.id,
                title=title,
                subject=subject,
                grade_level=grade_level,
                description=description,
                materials_needed=materials_needed,
                duration=duration,
                learning_objectives=learning_objectives,
                display_order=lesson_count
            )
            db.session.add(lesson)
            db.session.commit()

            logger.info(f'User {current_user.username} added favorite lesson: {title}')
            return jsonify({'success': True, 'lesson_id': lesson.id})

        except Exception as e:
            logger.error(f'Error adding favorite lesson: {e}')
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/profile/lessons/<int:lesson_id>/delete', methods=['POST'])
    @login_required
    def delete_favorite_lesson(lesson_id):
        """Delete a favorite lesson."""
        from flask import jsonify
        from app.models import FavoriteLesson

        try:
            lesson = FavoriteLesson.query.filter_by(id=lesson_id, user_id=current_user.id).first()
            if not lesson:
                return jsonify({'success': False, 'error': 'Lesson not found'}), 404

            db.session.delete(lesson)
            db.session.commit()

            logger.info(f'User {current_user.username} deleted favorite lesson {lesson_id}')
            return jsonify({'success': True})

        except Exception as e:
            logger.error(f'Error deleting favorite lesson: {e}')
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
