"""
Review and Rating routes for Teaching Resources Hub.

Allows teachers to review and rate educational resources, vote on helpful reviews,
and view aggregated ratings.
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.models import db, Review, ReviewHelpful, Activity
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


def register_review_routes(bp):
    """Register review routes to the blueprint."""

    @bp.route('/reviews/<resource_name>')
    def view_reviews(resource_name):
        """View all reviews for a specific resource."""
        logger.info(f"Viewing reviews for resource: {resource_name}")

        try:
            # Get all reviews for this resource, ordered by most helpful first
            reviews = Review.query.filter_by(
                resource_name=resource_name
            ).order_by(
                Review.helpful_votes.desc(),
                Review.created_at.desc()
            ).all()

            # Calculate average rating
            if reviews:
                avg_rating = sum(r.rating for r in reviews) / len(reviews)
                rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                for review in reviews:
                    rating_distribution[review.rating] += 1
            else:
                avg_rating = 0
                rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

            # Check which reviews the current user has marked as helpful
            helpful_review_ids = []
            if current_user.is_authenticated:
                helpful_votes = ReviewHelpful.query.filter_by(
                    user_id=current_user.id
                ).all()
                helpful_review_ids = [v.review_id for v in helpful_votes]

            return render_template('reviews/view_reviews.html',
                                 resource_name=resource_name,
                                 reviews=reviews,
                                 avg_rating=round(avg_rating, 1),
                                 total_reviews=len(reviews),
                                 rating_distribution=rating_distribution,
                                 helpful_review_ids=helpful_review_ids)

        except Exception as e:
            logger.error(f"Error viewing reviews for {resource_name}: {e}", exc_info=True)
            abort(500)

    @bp.route('/review/write/<resource_name>', methods=['GET', 'POST'])
    @login_required
    def write_review(resource_name):
        """Write a review for a resource."""
        if request.method == 'GET':
            # Get resource details from query params
            resource_url = request.args.get('url', '')
            resource_category = request.args.get('category', '')

            # Check if user already reviewed this resource
            existing_review = Review.query.filter_by(
                user_id=current_user.id,
                resource_name=resource_name
            ).first()

            if existing_review:
                flash('You have already reviewed this resource. You can edit your existing review.', 'info')
                return redirect(url_for('main.edit_review', review_id=existing_review.id))

            return render_template('reviews/write_review.html',
                                 resource_name=resource_name,
                                 resource_url=resource_url,
                                 resource_category=resource_category)

        # POST - Submit review
        try:
            rating = int(request.form.get('rating', 0))
            title = request.form.get('title', '').strip()
            review_text = request.form.get('review_text', '').strip()
            grade_level_used = request.form.get('grade_level_used', '').strip()
            subject_used = request.form.get('subject_used', '').strip()
            time_used = request.form.get('time_used', '').strip()
            resource_url = request.form.get('resource_url', '').strip()
            resource_category = request.form.get('resource_category', '').strip()

            # Validation
            errors = []
            if not rating or rating < 1 or rating > 5:
                errors.append('Please select a rating from 1 to 5 stars.')
            if not review_text or len(review_text) < 20:
                errors.append('Review must be at least 20 characters long.')
            if len(review_text) > 5000:
                errors.append('Review must be less than 5000 characters.')

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(request.url)

            # Create review
            review = Review(
                user_id=current_user.id,
                resource_name=resource_name,
                resource_category=resource_category,
                resource_url=resource_url,
                rating=rating,
                title=title,
                review_text=review_text,
                grade_level_used=grade_level_used,
                subject_used=subject_used,
                time_used=time_used
            )

            db.session.add(review)

            # Update user stats
            current_user.total_reviews += 1
            current_user.reputation_score += 10  # Award points for writing a review

            # Create activity
            activity = Activity(
                user_id=current_user.id,
                activity_type='review',
                related_resource_name=resource_name,
                related_resource_url=resource_url,
                activity_data=json.dumps({
                    'rating': rating,
                    'title': title
                })
            )
            db.session.add(activity)

            db.session.commit()

            flash('Your review has been posted! Thank you for contributing to the community.', 'success')
            logger.info(f"User {current_user.username} posted a review for {resource_name}")

            return redirect(url_for('main.view_reviews', resource_name=resource_name))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating review: {e}", exc_info=True)
            flash('An error occurred while posting your review. Please try again.', 'danger')
            return redirect(request.url)

    @bp.route('/review/<int:review_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_review(review_id):
        """Edit an existing review."""
        review = Review.query.get_or_404(review_id)

        # Check ownership
        if review.user_id != current_user.id:
            flash('You can only edit your own reviews.', 'danger')
            return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

        if request.method == 'GET':
            return render_template('reviews/edit_review.html', review=review)

        # POST - Update review
        try:
            rating = int(request.form.get('rating', 0))
            title = request.form.get('title', '').strip()
            review_text = request.form.get('review_text', '').strip()
            grade_level_used = request.form.get('grade_level_used', '').strip()
            subject_used = request.form.get('subject_used', '').strip()
            time_used = request.form.get('time_used', '').strip()

            # Validation
            errors = []
            if not rating or rating < 1 or rating > 5:
                errors.append('Please select a rating from 1 to 5 stars.')
            if not review_text or len(review_text) < 20:
                errors.append('Review must be at least 20 characters long.')

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(request.url)

            # Update review
            review.rating = rating
            review.title = title
            review.review_text = review_text
            review.grade_level_used = grade_level_used
            review.subject_used = subject_used
            review.time_used = time_used
            review.updated_at = datetime.utcnow()

            db.session.commit()

            flash('Your review has been updated.', 'success')
            return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating review: {e}", exc_info=True)
            flash('An error occurred while updating your review.', 'danger')
            return redirect(request.url)

    @bp.route('/review/<int:review_id>/delete', methods=['POST'])
    @login_required
    def delete_review(review_id):
        """Delete a review."""
        review = Review.query.get_or_404(review_id)

        # Check ownership or moderator
        if review.user_id != current_user.id and not current_user.is_moderator:
            flash('You can only delete your own reviews.', 'danger')
            return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

        try:
            resource_name = review.resource_name
            db.session.delete(review)

            # Update user stats
            if review.user_id == current_user.id:
                current_user.total_reviews = max(0, current_user.total_reviews - 1)

            db.session.commit()

            flash('Review deleted.', 'success')
            return redirect(url_for('main.view_reviews', resource_name=resource_name))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting review: {e}", exc_info=True)
            flash('An error occurred while deleting the review.', 'danger')
            return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

    @bp.route('/review/<int:review_id>/helpful', methods=['POST'])
    @login_required
    def mark_helpful(review_id):
        """Mark a review as helpful."""
        try:
            review = Review.query.get_or_404(review_id)

            # Check if user already marked this as helpful
            existing_vote = ReviewHelpful.query.filter_by(
                review_id=review_id,
                user_id=current_user.id
            ).first()

            if existing_vote:
                # Remove the helpful vote (toggle)
                db.session.delete(existing_vote)
                review.helpful_votes = max(0, review.helpful_votes - 1)
                action = 'removed'
            else:
                # Add helpful vote
                helpful_vote = ReviewHelpful(
                    review_id=review_id,
                    user_id=current_user.id
                )
                db.session.add(helpful_vote)
                review.helpful_votes += 1

                # Award points to review author
                review.author.helpful_votes_received += 1
                review.author.reputation_score += 2

                action = 'added'

            db.session.commit()

            if request.is_json:
                return jsonify({
                    'success': True,
                    'helpful_votes': review.helpful_votes,
                    'action': action
                })
            else:
                flash('Thank you for your feedback!', 'success')
                return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error marking review as helpful: {e}", exc_info=True)
            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500
            else:
                flash('An error occurred. Please try again.', 'danger')
                return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

    @bp.route('/review/<int:review_id>/report', methods=['POST'])
    @login_required
    def report_review(review_id):
        """Report a review for moderation."""
        try:
            review = Review.query.get_or_404(review_id)
            review.reported = True
            db.session.commit()

            flash('Review has been reported to moderators. Thank you.', 'success')
            logger.info(f"Review {review_id} reported by user {current_user.username}")

            return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reporting review: {e}", exc_info=True)
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('main.view_reviews', resource_name=review.resource_name))

    @bp.route('/api/reviews/resource/<resource_name>')
    def api_get_reviews(resource_name):
        """API endpoint to get reviews for a resource."""
        try:
            reviews = Review.query.filter_by(
                resource_name=resource_name
            ).order_by(Review.helpful_votes.desc()).all()

            reviews_data = []
            for review in reviews:
                reviews_data.append({
                    'id': review.id,
                    'author': review.author.username,
                    'author_display_name': review.author.display_name or review.author.username,
                    'rating': review.rating,
                    'title': review.title,
                    'review_text': review.review_text,
                    'grade_level_used': review.grade_level_used,
                    'subject_used': review.subject_used,
                    'time_used': review.time_used,
                    'helpful_votes': review.helpful_votes,
                    'created_at': review.created_at.isoformat(),
                    'updated_at': review.updated_at.isoformat() if review.updated_at else None
                })

            avg_rating = sum(r['rating'] for r in reviews_data) / len(reviews_data) if reviews_data else 0

            return jsonify({
                'success': True,
                'reviews': reviews_data,
                'total_reviews': len(reviews_data),
                'average_rating': round(avg_rating, 1)
            })

        except Exception as e:
            logger.error(f"Error fetching reviews via API: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
