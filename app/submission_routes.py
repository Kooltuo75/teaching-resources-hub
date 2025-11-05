"""
Resource Submission routes for Teaching Resources Hub.

Allows teachers to submit new resources for approval and moderators to review submissions.
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.models import db, ResourceSubmission, Activity, User
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


def register_submission_routes(bp):
    """Register resource submission routes to the blueprint."""

    @bp.route('/submit-resource', methods=['GET', 'POST'])
    @login_required
    def submit_resource():
        """Submit a new resource for approval."""
        if request.method == 'GET':
            return render_template('submissions/submit_resource.html')

        # POST - Submit resource
        try:
            name = request.form.get('name', '').strip()
            url = request.form.get('url', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            suggested_grade_levels = request.form.get('grade_levels', '').strip()
            tags = request.form.get('tags', '').strip()
            cost = request.form.get('cost', 'Free')
            why_useful = request.form.get('why_useful', '').strip()

            # Validation
            errors = []
            if not name or len(name) < 3:
                errors.append('Resource name must be at least 3 characters.')
            if not url or not (url.startswith('http://') or url.startswith('https://')):
                errors.append('Please provide a valid URL starting with http:// or https://')
            if not description or len(description) < 20:
                errors.append('Description must be at least 20 characters.')
            if not category:
                errors.append('Please select a category.')
            if not why_useful or len(why_useful) < 10:
                errors.append('Please explain why this resource is useful (at least 10 characters).')

            if errors:
                for error in errors:
                    flash(error, 'danger')
                return redirect(request.url)

            # Check for duplicate submissions
            existing = ResourceSubmission.query.filter_by(
                url=url,
                user_id=current_user.id
            ).first()

            if existing:
                flash('You have already submitted this resource. Please wait for review.', 'info')
                return redirect(url_for('main.my_submissions'))

            # Create submission
            submission = ResourceSubmission(
                user_id=current_user.id,
                name=name,
                url=url,
                description=description,
                category=category,
                suggested_grade_levels=suggested_grade_levels,
                tags=tags,
                cost=cost,
                why_useful=why_useful,
                status='pending'
            )

            db.session.add(submission)

            # Update user stats
            current_user.total_submissions += 1
            current_user.reputation_score += 5  # Award points for submission

            # Create activity
            activity = Activity(
                user_id=current_user.id,
                activity_type='submission',
                related_resource_name=name,
                related_resource_url=url,
                activity_data=json.dumps({
                    'category': category,
                    'status': 'pending'
                })
            )
            db.session.add(activity)

            db.session.commit()

            flash('Resource submitted successfully! It will be reviewed by moderators.', 'success')
            logger.info(f"User {current_user.username} submitted resource: {name}")

            return redirect(url_for('main.my_submissions'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error submitting resource: {e}", exc_info=True)
            flash('An error occurred while submitting the resource. Please try again.', 'danger')
            return redirect(request.url)

    @bp.route('/my-submissions')
    @login_required
    def my_submissions():
        """View the current user's resource submissions."""
        try:
            submissions = ResourceSubmission.query.filter_by(
                user_id=current_user.id
            ).order_by(ResourceSubmission.submitted_at.desc()).all()

            # Count by status
            status_counts = {
                'pending': sum(1 for s in submissions if s.status == 'pending'),
                'approved': sum(1 for s in submissions if s.status == 'approved'),
                'rejected': sum(1 for s in submissions if s.status == 'rejected')
            }

            return render_template('submissions/my_submissions.html',
                                 submissions=submissions,
                                 status_counts=status_counts)

        except Exception as e:
            logger.error(f"Error loading submissions: {e}", exc_info=True)
            abort(500)

    @bp.route('/submissions/moderate')
    @login_required
    def moderate_submissions():
        """Moderation page for reviewing submissions (moderators only)."""
        if not current_user.is_moderator:
            flash('You must be a moderator to access this page.', 'danger')
            return redirect(url_for('main.index'))

        try:
            # Get filter from query params
            status_filter = request.args.get('status', 'pending')

            submissions = ResourceSubmission.query

            if status_filter != 'all':
                submissions = submissions.filter_by(status=status_filter)

            submissions = submissions.order_by(
                ResourceSubmission.submitted_at.asc()
            ).all()

            # Count by status
            total_pending = ResourceSubmission.query.filter_by(status='pending').count()
            total_approved = ResourceSubmission.query.filter_by(status='approved').count()
            total_rejected = ResourceSubmission.query.filter_by(status='rejected').count()

            return render_template('submissions/moderate.html',
                                 submissions=submissions,
                                 status_filter=status_filter,
                                 total_pending=total_pending,
                                 total_approved=total_approved,
                                 total_rejected=total_rejected)

        except Exception as e:
            logger.error(f"Error loading moderation page: {e}", exc_info=True)
            abort(500)

    @bp.route('/submission/<int:submission_id>/approve', methods=['POST'])
    @login_required
    def approve_submission(submission_id):
        """Approve a resource submission (moderators only)."""
        if not current_user.is_moderator:
            flash('You must be a moderator to perform this action.', 'danger')
            return redirect(url_for('main.index'))

        try:
            submission = ResourceSubmission.query.get_or_404(submission_id)

            submission.status = 'approved'
            submission.reviewed_by = current_user.id
            submission.reviewed_at = datetime.utcnow()

            # Award points to submitter
            submitter = User.query.get(submission.user_id)
            if submitter:
                submitter.reputation_score += 20  # Bonus for approved submission

            db.session.commit()

            flash(f'Resource "{submission.name}" has been approved!', 'success')
            logger.info(f"Moderator {current_user.username} approved submission {submission_id}")

            # TODO: Add the resource to the main resources.json file here
            # This would require reading the JSON, adding the resource, and writing it back

            return redirect(url_for('main.moderate_submissions'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error approving submission: {e}", exc_info=True)
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('main.moderate_submissions'))

    @bp.route('/submission/<int:submission_id>/reject', methods=['POST'])
    @login_required
    def reject_submission(submission_id):
        """Reject a resource submission (moderators only)."""
        if not current_user.is_moderator:
            flash('You must be a moderator to perform this action.', 'danger')
            return redirect(url_for('main.index'))

        try:
            submission = ResourceSubmission.query.get_or_404(submission_id)
            reason = request.form.get('reason', '').strip()

            submission.status = 'rejected'
            submission.reviewed_by = current_user.id
            submission.reviewed_at = datetime.utcnow()
            submission.rejection_reason = reason

            db.session.commit()

            flash(f'Resource "{submission.name}" has been rejected.', 'success')
            logger.info(f"Moderator {current_user.username} rejected submission {submission_id}")

            return redirect(url_for('main.moderate_submissions'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error rejecting submission: {e}", exc_info=True)
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('main.moderate_submissions'))

    @bp.route('/submission/<int:submission_id>/delete', methods=['POST'])
    @login_required
    def delete_submission(submission_id):
        """Delete a resource submission."""
        submission = ResourceSubmission.query.get_or_404(submission_id)

        # Check ownership or moderator
        if submission.user_id != current_user.id and not current_user.is_moderator:
            flash('You can only delete your own submissions.', 'danger')
            return redirect(url_for('main.my_submissions'))

        try:
            db.session.delete(submission)

            # Update user stats if they're deleting their own
            if submission.user_id == current_user.id:
                current_user.total_submissions = max(0, current_user.total_submissions - 1)

            db.session.commit()

            flash('Submission deleted.', 'success')
            return redirect(url_for('main.my_submissions'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting submission: {e}", exc_info=True)
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('main.my_submissions'))

    @bp.route('/api/submissions/stats')
    @login_required
    def api_submission_stats():
        """API endpoint for submission statistics."""
        if not current_user.is_moderator:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        try:
            total_pending = ResourceSubmission.query.filter_by(status='pending').count()
            total_approved = ResourceSubmission.query.filter_by(status='approved').count()
            total_rejected = ResourceSubmission.query.filter_by(status='rejected').count()
            total_all = total_pending + total_approved + total_rejected

            # Top contributors
            from sqlalchemy import func
            top_contributors = db.session.query(
                User.username,
                User.display_name,
                func.count(ResourceSubmission.id).label('submission_count')
            ).join(
                ResourceSubmission, User.id == ResourceSubmission.user_id
            ).filter(
                ResourceSubmission.status == 'approved'
            ).group_by(
                User.id
            ).order_by(
                func.count(ResourceSubmission.id).desc()
            ).limit(10).all()

            return jsonify({
                'success': True,
                'stats': {
                    'pending': total_pending,
                    'approved': total_approved,
                    'rejected': total_rejected,
                    'total': total_all
                },
                'top_contributors': [
                    {
                        'username': c.username,
                        'display_name': c.display_name or c.username,
                        'count': c.submission_count
                    } for c in top_contributors
                ]
            })

        except Exception as e:
            logger.error(f"Error fetching submission stats: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
