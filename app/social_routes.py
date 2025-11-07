"""
Social features routes for Teaching Resources Hub.

Allows teachers to follow each other, view activity feeds, and discover other teachers.
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.models import db, User, Follow, Activity, Review, Favorite, TeachingJourneyEvent, ClassroomPhoto, FavoriteLesson
from sqlalchemy import or_, desc, func
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


def register_social_routes(bp):
    """Register social feature routes to the blueprint."""

    @bp.route('/feed')
    @login_required
    def activity_feed():
        """View activity feed from people you follow."""
        try:
            # Get list of users the current user is following
            following_ids = [f.followed_id for f in current_user.following.all()]

            if not following_ids:
                # No following yet, show global feed or recommendations
                activities = Activity.query.filter_by(
                    is_public=True
                ).order_by(Activity.created_at.desc()).limit(50).all()

                return render_template('social/activity_feed.html',
                                     activities=activities,
                                     is_empty=True,
                                     following_count=0)

            # Get activities from followed users
            activities = Activity.query.filter(
                Activity.user_id.in_(following_ids),
                Activity.is_public == True
            ).order_by(Activity.created_at.desc()).limit(100).all()

            return render_template('social/activity_feed.html',
                                 activities=activities,
                                 is_empty=False,
                                 following_count=len(following_ids))

        except Exception as e:
            logger.error(f"Error loading activity feed: {e}", exc_info=True)
            abort(500)

    @bp.route('/discover')
    def discover_teachers():
        """Discover other teachers on the platform."""
        try:
            # Get filter parameters
            grade_level = request.args.get('grade_level', '')
            subject = request.args.get('subject', '')
            sort_by = request.args.get('sort', 'active')  # active, reviews, followers

            # Base query
            teachers = User.query.filter(
                User.profile_public == True
            )

            # Apply filters
            if grade_level:
                teachers = teachers.filter(User.grade_level.contains(grade_level))

            if subject:
                teachers = teachers.filter(User.subjects_taught.contains(subject))

            # Apply sorting
            if sort_by == 'reviews':
                teachers = teachers.order_by(User.total_reviews.desc())
            elif sort_by == 'followers':
                # Count followers - simplified approach for SQLAlchemy 2.0 compatibility
                # Instead of complex subquery, just order by reputation or let frontend handle it
                teachers = teachers.order_by(User.reputation_score.desc())
            else:  # active
                teachers = teachers.order_by(User.last_login.desc().nulls_last())

            # Pagination
            page = request.args.get('page', 1, type=int)
            per_page = 24
            teachers_paginated = teachers.paginate(page=page, per_page=per_page, error_out=False)

            # Get following status for each teacher
            following_ids = []
            if current_user.is_authenticated:
                try:
                    following_ids = [f.followed_id for f in current_user.following.all()]
                except Exception as e:
                    logger.debug(f"Could not load following list: {e}")
                    following_ids = []

            # Enhance each teacher with Phase 2 data and following status
            teachers_with_data = []
            for teacher in teachers_paginated.items:
                # Add is_following flag
                teacher.is_following = teacher.id in following_ids

                # Load Phase 2 content counts
                if hasattr(teacher, 'id'):
                    try:
                        teacher.timeline_count = TeachingJourneyEvent.query.filter_by(user_id=teacher.id).count()
                        teacher.photo_count = ClassroomPhoto.query.filter_by(user_id=teacher.id).count()
                        teacher.lesson_count = FavoriteLesson.query.filter_by(user_id=teacher.id).count()

                        # Get latest photo for preview
                        teacher.latest_photo = ClassroomPhoto.query.filter_by(user_id=teacher.id).order_by(
                            ClassroomPhoto.uploaded_at.desc()
                        ).first()

                        # Get current teaching unit
                        teacher.has_current_unit = (
                            hasattr(teacher, 'current_unit_title') and
                            teacher.current_unit_title
                        )
                    except Exception as e:
                        logger.debug(f"Error loading Phase 2 data for teacher {teacher.id}: {e}")
                        teacher.timeline_count = 0
                        teacher.photo_count = 0
                        teacher.lesson_count = 0
                        teacher.latest_photo = None
                        teacher.has_current_unit = False

                teachers_with_data.append(teacher)

            return render_template('social/discover.html',
                                 teachers=teachers_with_data,
                                 page=page,
                                 total_pages=teachers_paginated.pages,
                                 pagination=teachers_paginated,
                                 following_ids=following_ids,
                                 grade_level=grade_level,
                                 subject=subject,
                                 sort_by=sort_by)

        except Exception as e:
            logger.error(f"Error in discover page: {e}", exc_info=True)
            # Make page fault-tolerant - show empty results instead of crashing
            try:
                return render_template('social/discover.html',
                                     teachers=[],
                                     pagination=None,
                                     following_ids=[],
                                     grade_level='',
                                     subject='',
                                     sort_by='active',
                                     error_message='Unable to load teachers at this time. Please try again later.')
            except:
                abort(500)

    @bp.route('/user/<username>/follow', methods=['POST'])
    @login_required
    def follow_user(username):
        """Follow a user."""
        try:
            user_to_follow = User.query.filter_by(username=username).first_or_404()

            # Can't follow yourself
            if user_to_follow.id == current_user.id:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Cannot follow yourself'}), 400
                flash('You cannot follow yourself.', 'warning')
                return redirect(url_for('main.view_profile', username=username))

            # Check if already following
            if current_user.is_following(user_to_follow):
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Already following'}), 400
                flash(f'You are already following {user_to_follow.display_name or username}.', 'info')
                return redirect(url_for('main.view_profile', username=username))

            # Follow the user
            current_user.follow(user_to_follow)

            # Create activity
            activity = Activity(
                user_id=current_user.id,
                activity_type='follow',
                related_user_id=user_to_follow.id,
                activity_data=json.dumps({
                    'followed_username': username,
                    'followed_display_name': user_to_follow.display_name
                })
            )
            db.session.add(activity)

            # Award reputation points
            current_user.reputation_score += 1
            user_to_follow.reputation_score += 3  # Being followed is worth more

            db.session.commit()

            if request.is_json:
                return jsonify({
                    'success': True,
                    'follower_count': user_to_follow.get_follower_count()
                })

            flash(f'You are now following {user_to_follow.display_name or username}!', 'success')
            logger.info(f"User {current_user.username} followed {username}")

            return redirect(url_for('main.view_profile', username=username))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error following user: {e}", exc_info=True)
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('main.discover_teachers'))

    @bp.route('/user/<username>/unfollow', methods=['POST'])
    @login_required
    def unfollow_user(username):
        """Unfollow a user."""
        try:
            user_to_unfollow = User.query.filter_by(username=username).first_or_404()

            if not current_user.is_following(user_to_unfollow):
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Not following'}), 400
                flash(f'You are not following {user_to_unfollow.display_name or username}.', 'info')
                return redirect(url_for('main.view_profile', username=username))

            # Unfollow the user
            current_user.unfollow(user_to_unfollow)
            db.session.commit()

            if request.is_json:
                return jsonify({
                    'success': True,
                    'follower_count': user_to_unfollow.get_follower_count()
                })

            flash(f'You have unfollowed {user_to_unfollow.display_name or username}.', 'success')
            logger.info(f"User {current_user.username} unfollowed {username}")

            return redirect(url_for('main.view_profile', username=username))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error unfollowing user: {e}", exc_info=True)
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('main.view_profile', username=username))

    @bp.route('/user/<username>/followers')
    def view_followers(username):
        """View a user's followers."""
        try:
            user = User.query.filter_by(username=username).first_or_404()

            # Get followers
            followers = db.session.query(User).join(
                Follow, Follow.follower_id == User.id
            ).filter(
                Follow.followed_id == user.id
            ).order_by(Follow.created_at.desc()).all()

            # Check if current user is following each follower
            following_ids = []
            if current_user.is_authenticated:
                following_ids = [f.followed_id for f in current_user.following.all()]

            return render_template('social/followers.html',
                                 user=user,
                                 followers=followers,
                                 following_ids=following_ids,
                                 is_followers=True)

        except Exception as e:
            logger.error(f"Error viewing followers: {e}", exc_info=True)
            abort(500)

    @bp.route('/user/<username>/following')
    def view_following(username):
        """View users that a user is following."""
        try:
            user = User.query.filter_by(username=username).first_or_404()

            # Get following
            following = db.session.query(User).join(
                Follow, Follow.followed_id == User.id
            ).filter(
                Follow.follower_id == user.id
            ).order_by(Follow.created_at.desc()).all()

            # Check if current user is following each person
            following_ids = []
            if current_user.is_authenticated:
                following_ids = [f.followed_id for f in current_user.following.all()]

            return render_template('social/followers.html',
                                 user=user,
                                 followers=following,  # Reuse same template
                                 following_ids=following_ids,
                                 is_followers=False)

        except Exception as e:
            logger.error(f"Error viewing following: {e}", exc_info=True)
            abort(500)

    @bp.route('/leaderboard')
    def leaderboard():
        """View reputation leaderboard."""
        try:
            # Get filter
            timeframe = request.args.get('timeframe', 'all')  # all, month, week
            category = request.args.get('category', 'reputation')  # reputation, reviews, submissions

            # Base query
            users = User.query.filter(User.profile_public == True)

            # Order by category
            if category == 'reviews':
                users = users.order_by(User.total_reviews.desc())
            elif category == 'submissions':
                users = users.order_by(User.total_submissions.desc())
            else:  # reputation
                users = users.order_by(User.reputation_score.desc())

            # Limit to top 100
            top_users = users.limit(100).all()

            # Calculate ranks
            users_with_ranks = []
            for rank, user in enumerate(top_users, 1):
                users_with_ranks.append({
                    'rank': rank,
                    'user': user
                })

            # Find current user's rank if authenticated
            current_user_rank = None
            if current_user.is_authenticated:
                for item in users_with_ranks:
                    if item['user'].id == current_user.id:
                        current_user_rank = item['rank']
                        break

            return render_template('social/leaderboard.html',
                                 users=users_with_ranks,
                                 category=category,
                                 timeframe=timeframe,
                                 current_user_rank=current_user_rank)

        except Exception as e:
            logger.error(f"Error loading leaderboard: {e}", exc_info=True)
            abort(500)

    @bp.route('/api/user/<username>/stats')
    def api_user_stats(username):
        """API endpoint for user statistics."""
        try:
            user = User.query.filter_by(username=username).first_or_404()

            # Recent activity count
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_reviews = Review.query.filter(
                Review.user_id == user.id,
                Review.created_at >= week_ago
            ).count()

            recent_activities = Activity.query.filter(
                Activity.user_id == user.id,
                Activity.created_at >= week_ago
            ).count()

            return jsonify({
                'success': True,
                'stats': {
                    'reputation_score': user.reputation_score,
                    'total_reviews': user.total_reviews,
                    'total_submissions': user.total_submissions,
                    'helpful_votes_received': user.helpful_votes_received,
                    'followers': user.get_follower_count(),
                    'following': user.get_following_count(),
                    'recent_reviews_7d': recent_reviews,
                    'recent_activities_7d': recent_activities,
                    'is_moderator': user.is_moderator,
                    'is_verified_teacher': user.is_verified_teacher
                }
            })

        except Exception as e:
            logger.error(f"Error fetching user stats: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
