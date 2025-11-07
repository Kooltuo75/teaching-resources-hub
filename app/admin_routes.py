"""
Admin Dashboard and Moderation Routes for Teaching Resources Hub.

Provides admin-only functionality for:
- User management (verify, ban, edit)
- Site analytics and metrics
- Content moderation
- System settings
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from functools import wraps
from app.models import db, User, Review, Favorite, Activity, Follow, TeachingJourneyEvent, ClassroomPhoto, FavoriteLesson
from sqlalchemy import func, desc, or_
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def admin_required(f):
    """
    Decorator to require admin or moderator access.
    Use this on any route that should only be accessible to admins.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login'))

        if not (current_user.is_admin or current_user.is_moderator):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


def register_admin_routes(bp):
    """Register admin routes to the blueprint."""

    @bp.route('/admin')
    @login_required
    @admin_required
    def admin_dashboard():
        """Main admin dashboard with overview metrics."""
        try:
            # User statistics
            total_users = User.query.count()
            verified_teachers = User.query.filter_by(is_verified_teacher=True).count()
            moderators = User.query.filter_by(is_moderator=True).count()

            # New users in last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            new_users_week = User.query.filter(User.created_at >= week_ago).count()

            # New users in last 30 days
            month_ago = datetime.utcnow() - timedelta(days=30)
            new_users_month = User.query.filter(User.created_at >= month_ago).count()

            # Content statistics
            total_reviews = Review.query.count()
            total_favorites = Favorite.query.count()
            total_timeline_events = TeachingJourneyEvent.query.count()
            total_photos = ClassroomPhoto.query.count()
            total_lessons = FavoriteLesson.query.count()

            # Recent activity
            recent_reviews_week = Review.query.filter(Review.created_at >= week_ago).count()
            recent_activities_week = Activity.query.filter(Activity.created_at >= week_ago).count()

            # Follow statistics
            total_follows = Follow.query.count()

            # Most active users (by reputation)
            top_users = User.query.order_by(User.reputation_score.desc()).limit(10).all()

            # Recent users (last 20)
            recent_users = User.query.order_by(User.created_at.desc()).limit(20).all()

            # Users needing verification (profile_public but not verified)
            pending_verification = User.query.filter(
                User.profile_public == True,
                User.is_verified_teacher == False
            ).order_by(User.created_at.desc()).limit(10).all()

            return render_template('admin/dashboard.html',
                                 total_users=total_users,
                                 verified_teachers=verified_teachers,
                                 moderators=moderators,
                                 new_users_week=new_users_week,
                                 new_users_month=new_users_month,
                                 total_reviews=total_reviews,
                                 total_favorites=total_favorites,
                                 total_timeline_events=total_timeline_events,
                                 total_photos=total_photos,
                                 total_lessons=total_lessons,
                                 recent_reviews_week=recent_reviews_week,
                                 recent_activities_week=recent_activities_week,
                                 total_follows=total_follows,
                                 top_users=top_users,
                                 recent_users=recent_users,
                                 pending_verification=pending_verification)

        except Exception as e:
            logger.error(f"Error loading admin dashboard: {e}", exc_info=True)
            flash('Error loading dashboard. Please try again.', 'danger')
            return redirect(url_for('main.index'))

    @bp.route('/admin/users')
    @login_required
    @admin_required
    def admin_users():
        """User management page with search and filters."""
        try:
            # Get search and filter parameters
            search = request.args.get('search', '').strip()
            filter_type = request.args.get('filter', 'all')  # all, verified, unverified, moderators, banned
            sort_by = request.args.get('sort', 'newest')  # newest, oldest, active, reputation

            # Base query
            query = User.query

            # Apply search
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        User.username.ilike(search_term),
                        User.email.ilike(search_term),
                        User.display_name.ilike(search_term)
                    )
                )

            # Apply filters
            if filter_type == 'verified':
                query = query.filter_by(is_verified_teacher=True)
            elif filter_type == 'unverified':
                query = query.filter_by(is_verified_teacher=False)
            elif filter_type == 'moderators':
                query = query.filter(
                    or_(User.is_moderator == True, User.is_admin == True)
                )
            elif filter_type == 'banned':
                query = query.filter_by(is_banned=True)

            # Apply sorting
            if sort_by == 'oldest':
                query = query.order_by(User.created_at.asc())
            elif sort_by == 'active':
                query = query.order_by(User.last_login.desc().nulls_last())
            elif sort_by == 'reputation':
                query = query.order_by(User.reputation_score.desc())
            else:  # newest
                query = query.order_by(User.created_at.desc())

            # Pagination
            page = request.args.get('page', 1, type=int)
            per_page = 50
            users_paginated = query.paginate(page=page, per_page=per_page, error_out=False)

            return render_template('admin/users.html',
                                 users=users_paginated.items,
                                 pagination=users_paginated,
                                 page=page,
                                 total_pages=users_paginated.pages,
                                 search=search,
                                 filter_type=filter_type,
                                 sort_by=sort_by)

        except Exception as e:
            logger.error(f"Error loading user management: {e}", exc_info=True)
            flash('Error loading users. Please try again.', 'danger')
            return redirect(url_for('main.admin_dashboard'))

    @bp.route('/admin/user/<int:user_id>/verify', methods=['POST'])
    @login_required
    @admin_required
    def admin_verify_user(user_id):
        """Verify a teacher (mark as verified)."""
        try:
            user = User.query.get_or_404(user_id)

            user.is_verified_teacher = True
            db.session.commit()

            logger.info(f"Admin {current_user.username} verified user {user.username}")

            if request.is_json:
                return jsonify({'success': True, 'message': 'User verified successfully'})

            flash(f'User {user.username} has been verified!', 'success')
            return redirect(request.referrer or url_for('main.admin_users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error verifying user: {e}", exc_info=True)

            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500

            flash('Error verifying user. Please try again.', 'danger')
            return redirect(url_for('main.admin_users'))

    @bp.route('/admin/user/<int:user_id>/unverify', methods=['POST'])
    @login_required
    @admin_required
    def admin_unverify_user(user_id):
        """Remove verification from a user."""
        try:
            user = User.query.get_or_404(user_id)

            user.is_verified_teacher = False
            db.session.commit()

            logger.info(f"Admin {current_user.username} unverified user {user.username}")

            if request.is_json:
                return jsonify({'success': True, 'message': 'Verification removed'})

            flash(f'Verification removed from {user.username}.', 'success')
            return redirect(request.referrer or url_for('main.admin_users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error unverifying user: {e}", exc_info=True)

            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500

            flash('Error removing verification. Please try again.', 'danger')
            return redirect(url_for('main.admin_users'))

    @bp.route('/admin/user/<int:user_id>/ban', methods=['POST'])
    @login_required
    @admin_required
    def admin_ban_user(user_id):
        """Ban a user from the platform."""
        try:
            user = User.query.get_or_404(user_id)

            # Can't ban admins
            if user.is_admin:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Cannot ban administrators'}), 400
                flash('Cannot ban administrators.', 'danger')
                return redirect(url_for('main.admin_users'))

            user.is_banned = True
            db.session.commit()

            logger.warning(f"Admin {current_user.username} banned user {user.username}")

            if request.is_json:
                return jsonify({'success': True, 'message': 'User banned successfully'})

            flash(f'User {user.username} has been banned.', 'success')
            return redirect(request.referrer or url_for('main.admin_users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error banning user: {e}", exc_info=True)

            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500

            flash('Error banning user. Please try again.', 'danger')
            return redirect(url_for('main.admin_users'))

    @bp.route('/admin/user/<int:user_id>/unban', methods=['POST'])
    @login_required
    @admin_required
    def admin_unban_user(user_id):
        """Unban a user."""
        try:
            user = User.query.get_or_404(user_id)

            user.is_banned = False
            db.session.commit()

            logger.info(f"Admin {current_user.username} unbanned user {user.username}")

            if request.is_json:
                return jsonify({'success': True, 'message': 'User unbanned successfully'})

            flash(f'User {user.username} has been unbanned.', 'success')
            return redirect(request.referrer or url_for('main.admin_users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error unbanning user: {e}", exc_info=True)

            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500

            flash('Error unbanning user. Please try again.', 'danger')
            return redirect(url_for('main.admin_users'))

    @bp.route('/admin/user/<int:user_id>/make-moderator', methods=['POST'])
    @login_required
    @admin_required
    def admin_make_moderator(user_id):
        """Promote a user to moderator (admin only)."""
        try:
            # Only admins can promote to moderator
            if not current_user.is_admin:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Only admins can promote moderators'}), 403
                flash('Only administrators can promote moderators.', 'danger')
                return redirect(url_for('main.admin_users'))

            user = User.query.get_or_404(user_id)

            user.is_moderator = True
            db.session.commit()

            logger.info(f"Admin {current_user.username} promoted {user.username} to moderator")

            if request.is_json:
                return jsonify({'success': True, 'message': 'User promoted to moderator'})

            flash(f'{user.username} is now a moderator!', 'success')
            return redirect(request.referrer or url_for('main.admin_users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error promoting to moderator: {e}", exc_info=True)

            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500

            flash('Error promoting user. Please try again.', 'danger')
            return redirect(url_for('main.admin_users'))

    @bp.route('/admin/user/<int:user_id>/remove-moderator', methods=['POST'])
    @login_required
    @admin_required
    def admin_remove_moderator(user_id):
        """Remove moderator status from a user (admin only)."""
        try:
            # Only admins can demote moderators
            if not current_user.is_admin:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Only admins can remove moderators'}), 403
                flash('Only administrators can remove moderators.', 'danger')
                return redirect(url_for('main.admin_users'))

            user = User.query.get_or_404(user_id)

            # Can't demote admins
            if user.is_admin:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Cannot remove admin status'}), 400
                flash('Cannot remove admin status.', 'danger')
                return redirect(url_for('main.admin_users'))

            user.is_moderator = False
            db.session.commit()

            logger.info(f"Admin {current_user.username} removed moderator status from {user.username}")

            if request.is_json:
                return jsonify({'success': True, 'message': 'Moderator status removed'})

            flash(f'Moderator status removed from {user.username}.', 'success')
            return redirect(request.referrer or url_for('main.admin_users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing moderator: {e}", exc_info=True)

            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500

            flash('Error removing moderator status. Please try again.', 'danger')
            return redirect(url_for('main.admin_users'))

    @bp.route('/admin/analytics')
    @login_required
    @admin_required
    def admin_analytics():
        """Analytics dashboard with charts and growth metrics."""
        try:
            # User growth data (last 30 days)
            user_growth = []
            for i in range(30, -1, -1):
                date = datetime.utcnow() - timedelta(days=i)
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date_start + timedelta(days=1)

                count = User.query.filter(
                    User.created_at >= date_start,
                    User.created_at < date_end
                ).count()

                user_growth.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'count': count
                })

            # Activity growth (last 30 days)
            activity_growth = []
            for i in range(30, -1, -1):
                date = datetime.utcnow() - timedelta(days=i)
                date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = date_start + timedelta(days=1)

                count = Activity.query.filter(
                    Activity.created_at >= date_start,
                    Activity.created_at < date_end
                ).count()

                activity_growth.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'count': count
                })

            # Top subjects by teacher count
            subject_counts = db.session.query(
                User.subjects_taught,
                func.count(User.id).label('count')
            ).filter(
                User.subjects_taught.isnot(None),
                User.subjects_taught != ''
            ).group_by(User.subjects_taught).order_by(desc('count')).limit(10).all()

            # Top grade levels by teacher count
            grade_counts = db.session.query(
                User.grade_level,
                func.count(User.id).label('count')
            ).filter(
                User.grade_level.isnot(None),
                User.grade_level != ''
            ).group_by(User.grade_level).order_by(desc('count')).limit(10).all()

            return render_template('admin/analytics.html',
                                 user_growth=user_growth,
                                 activity_growth=activity_growth,
                                 subject_counts=subject_counts,
                                 grade_counts=grade_counts)

        except Exception as e:
            logger.error(f"Error loading analytics: {e}", exc_info=True)
            flash('Error loading analytics. Please try again.', 'danger')
            return redirect(url_for('main.admin_dashboard'))
