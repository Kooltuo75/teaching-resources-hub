"""
Resource Upload and Management Routes for Teaching Resources Hub.

Handles:
- File uploads with validation
- Resource management (edit, delete)
- Browse and search resources
- Download tracking
- Resource collections
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, UploadedResource, ResourceDownload, ResourceCollection, CollectionItem
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# File upload configuration
UPLOAD_FOLDER = 'app/static/uploads/resources'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif', 'txt', 'zip'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file):
    """Get file size in bytes."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size


def register_resource_upload_routes(bp):
    """Register resource upload routes to the blueprint."""

    @bp.route('/my-resources')
    @login_required
    def my_resources():
        """View and manage user's uploaded resources."""
        try:
            resources = UploadedResource.query.filter_by(
                user_id=current_user.id
            ).order_by(UploadedResource.uploaded_at.desc()).all()

            # Get stats
            total_downloads = sum(r.download_count for r in resources)
            total_views = sum(r.view_count for r in resources)

            return render_template('resources/my_resources.html',
                                 resources=resources,
                                 total_downloads=total_downloads,
                                 total_views=total_views)

        except Exception as e:
            logger.error(f"Error loading my resources: {e}", exc_info=True)
            flash('Error loading resources. Please try again.', 'danger')
            return redirect(url_for('main.index'))

    @bp.route('/upload-resource', methods=['GET', 'POST'])
    @login_required
    def upload_resource():
        """Upload a new resource."""
        if request.method == 'POST':
            try:
                # Check if file is present
                if 'file' not in request.files:
                    flash('No file selected', 'danger')
                    return redirect(request.url)

                file = request.files['file']

                if file.filename == '':
                    flash('No file selected', 'danger')
                    return redirect(request.url)

                if not allowed_file(file.filename):
                    flash(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 'danger')
                    return redirect(request.url)

                # Check file size
                file_size = get_file_size(file)
                if file_size > MAX_FILE_SIZE:
                    flash(f'File too large. Maximum size is 50MB.', 'danger')
                    return redirect(request.url)

                # Secure filename and save
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                unique_filename = f"{current_user.id}_{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

                # Create directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                file.save(file_path)

                # Get file extension
                file_ext = filename.rsplit('.', 1)[1].lower()

                # Create database entry
                resource = UploadedResource(
                    user_id=current_user.id,
                    title=request.form.get('title', '').strip(),
                    description=request.form.get('description', '').strip(),
                    file_path=f'uploads/resources/{unique_filename}',
                    file_type=file_ext,
                    file_size=file_size,
                    category=request.form.get('category', '').strip(),
                    grade_level=request.form.get('grade_level', '').strip(),
                    tags=request.form.get('tags', '').strip(),
                    standards=request.form.get('standards', '').strip(),
                    duration=request.form.get('duration', '').strip(),
                    difficulty=request.form.get('difficulty', 'Medium'),
                    is_public=request.form.get('is_public', 'true') == 'true'
                )

                db.session.add(resource)
                db.session.commit()

                logger.info(f"User {current_user.username} uploaded resource: {resource.title}")
                flash(f'Resource "{resource.title}" uploaded successfully!', 'success')
                return redirect(url_for('main.my_resources'))

            except Exception as e:
                db.session.rollback()
                logger.error(f"Error uploading resource: {e}", exc_info=True)
                flash('Error uploading resource. Please try again.', 'danger')
                return redirect(request.url)

        # GET request - show upload form
        return render_template('resources/upload_resource.html')

    @bp.route('/resource/<int:resource_id>')
    def view_resource(resource_id):
        """View a single resource detail page."""
        try:
            resource = UploadedResource.query.get_or_404(resource_id)

            # Check if user has permission to view
            if not resource.is_public and (not current_user.is_authenticated or current_user.id != resource.user_id):
                abort(403)

            # Increment view count
            resource.view_count += 1
            db.session.commit()

            # Get uploader info
            from app.models import User
            uploader = User.query.get(resource.user_id)

            return render_template('resources/view_resource.html',
                                 resource=resource,
                                 uploader=uploader)

        except Exception as e:
            logger.error(f"Error viewing resource: {e}", exc_info=True)
            abort(404)

    @bp.route('/resource/<int:resource_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_resource(resource_id):
        """Edit a resource."""
        try:
            resource = UploadedResource.query.get_or_404(resource_id)

            # Check ownership
            if resource.user_id != current_user.id:
                flash('You do not have permission to edit this resource.', 'danger')
                return redirect(url_for('main.my_resources'))

            if request.method == 'POST':
                resource.title = request.form.get('title', '').strip()
                resource.description = request.form.get('description', '').strip()
                resource.category = request.form.get('category', '').strip()
                resource.grade_level = request.form.get('grade_level', '').strip()
                resource.tags = request.form.get('tags', '').strip()
                resource.standards = request.form.get('standards', '').strip()
                resource.duration = request.form.get('duration', '').strip()
                resource.difficulty = request.form.get('difficulty', 'Medium')
                resource.is_public = request.form.get('is_public', 'true') == 'true'

                db.session.commit()

                logger.info(f"User {current_user.username} edited resource: {resource.title}")
                flash('Resource updated successfully!', 'success')
                return redirect(url_for('main.my_resources'))

            return render_template('resources/edit_resource.html', resource=resource)

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error editing resource: {e}", exc_info=True)
            flash('Error editing resource. Please try again.', 'danger')
            return redirect(url_for('main.my_resources'))

    @bp.route('/resource/<int:resource_id>/delete', methods=['POST'])
    @login_required
    def delete_resource(resource_id):
        """Delete a resource."""
        try:
            resource = UploadedResource.query.get_or_404(resource_id)

            # Check ownership
            if resource.user_id != current_user.id:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Permission denied'}), 403
                flash('You do not have permission to delete this resource.', 'danger')
                return redirect(url_for('main.my_resources'))

            # Delete file from filesystem
            file_path = os.path.join('app/static', resource.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete from database
            db.session.delete(resource)
            db.session.commit()

            logger.info(f"User {current_user.username} deleted resource: {resource.title}")

            if request.is_json:
                return jsonify({'success': True, 'message': 'Resource deleted'})

            flash('Resource deleted successfully!', 'success')
            return redirect(url_for('main.my_resources'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting resource: {e}", exc_info=True)

            if request.is_json:
                return jsonify({'success': False, 'error': str(e)}), 500

            flash('Error deleting resource. Please try again.', 'danger')
            return redirect(url_for('main.my_resources'))

    @bp.route('/resource/<int:resource_id>/download')
    def download_resource(resource_id):
        """Download a resource and track the download."""
        try:
            resource = UploadedResource.query.get_or_404(resource_id)

            # Check if user has permission
            if not resource.is_public and (not current_user.is_authenticated or current_user.id != resource.user_id):
                abort(403)

            # Track download
            download = ResourceDownload(
                resource_id=resource.id,
                user_id=current_user.id if current_user.is_authenticated else None,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                referrer=request.referrer
            )
            db.session.add(download)

            # Increment download count
            resource.download_count += 1
            db.session.commit()

            # Send file
            directory = os.path.dirname(os.path.join('app/static', resource.file_path))
            filename = os.path.basename(resource.file_path)

            return send_from_directory(directory, filename, as_attachment=True)

        except Exception as e:
            logger.error(f"Error downloading resource: {e}", exc_info=True)
            abort(404)

    @bp.route('/browse-resources')
    def browse_resources():
        """Browse all public resources with search and filters."""
        try:
            # Get search and filter parameters
            search = request.args.get('search', '').strip()
            category = request.args.get('category', '')
            grade_level = request.args.get('grade_level', '')
            difficulty = request.args.get('difficulty', '')
            file_type = request.args.get('file_type', '')
            sort_by = request.args.get('sort', 'newest')  # newest, popular, downloads, rating

            # Base query - only public resources
            query = UploadedResource.query.filter_by(is_public=True)

            # Apply search
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    db.or_(
                        UploadedResource.title.ilike(search_term),
                        UploadedResource.description.ilike(search_term),
                        UploadedResource.tags.ilike(search_term)
                    )
                )

            # Apply filters
            if category:
                query = query.filter(UploadedResource.category == category)
            if grade_level:
                query = query.filter(UploadedResource.grade_level.contains(grade_level))
            if difficulty:
                query = query.filter(UploadedResource.difficulty == difficulty)
            if file_type:
                query = query.filter(UploadedResource.file_type == file_type)

            # Apply sorting
            if sort_by == 'popular':
                query = query.order_by(UploadedResource.view_count.desc())
            elif sort_by == 'downloads':
                query = query.order_by(UploadedResource.download_count.desc())
            elif sort_by == 'rating':
                query = query.order_by(UploadedResource.rating_sum.desc())
            else:  # newest
                query = query.order_by(UploadedResource.uploaded_at.desc())

            # Pagination
            page = request.args.get('page', 1, type=int)
            per_page = 24
            resources_paginated = query.paginate(page=page, per_page=per_page, error_out=False)

            # Get unique categories and file types for filter dropdowns
            categories = db.session.query(UploadedResource.category).filter(
                UploadedResource.category.isnot(None),
                UploadedResource.category != '',
                UploadedResource.is_public == True
            ).distinct().all()
            categories = [c[0] for c in categories]

            file_types = db.session.query(UploadedResource.file_type).filter(
                UploadedResource.file_type.isnot(None),
                UploadedResource.is_public == True
            ).distinct().all()
            file_types = [f[0] for f in file_types]

            return render_template('resources/browse_resources.html',
                                 resources=resources_paginated.items,
                                 pagination=resources_paginated,
                                 page=page,
                                 total_pages=resources_paginated.pages,
                                 search=search,
                                 category=category,
                                 grade_level=grade_level,
                                 difficulty=difficulty,
                                 file_type=file_type,
                                 sort_by=sort_by,
                                 categories=categories,
                                 file_types=file_types)

        except Exception as e:
            logger.error(f"Error browsing resources: {e}", exc_info=True)
            flash('Error loading resources. Please try again.', 'danger')
            return redirect(url_for('main.index'))
