"""
Google Classroom integration routes.
Allows teachers to share resources directly to Google Classroom.
"""

from flask import redirect, url_for, request, flash, jsonify, session, current_app
from flask_login import login_required, current_user
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import logging
import json

from app.models import db

logger = logging.getLogger(__name__)


def register_google_classroom_routes(bp):
    """Register Google Classroom routes to the blueprint."""

    def get_google_flow():
        """Create and return Google OAuth flow."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": current_app.config['GOOGLE_CLIENT_ID'],
                    "client_secret": current_app.config['GOOGLE_CLIENT_SECRET'],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [url_for('main.google_callback', _external=True)]
                }
            },
            scopes=current_app.config['GOOGLE_SCOPES']
        )
        flow.redirect_uri = url_for('main.google_callback', _external=True)
        return flow

    def get_google_credentials():
        """Get Google credentials for the current user."""
        if not current_user.google_access_token:
            return None

        creds_data = {
            'token': current_user.google_access_token,
            'refresh_token': current_user.google_refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'scopes': current_app.config['GOOGLE_SCOPES']
        }

        if current_user.google_token_expiry:
            creds_data['expiry'] = current_user.google_token_expiry.isoformat()

        return Credentials(**creds_data)

    @bp.route('/google/connect')
    @login_required
    def google_connect():
        """Initiate Google OAuth flow."""
        try:
            # Check if client ID is configured
            if current_app.config['GOOGLE_CLIENT_ID'] == 'YOUR_CLIENT_ID_HERE':
                flash('Google Classroom integration is not configured. Please see setup instructions.', 'error')
                return redirect(url_for('main.profile', username=current_user.username))

            flow = get_google_flow()
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )

            # Store state in session for verification
            session['google_auth_state'] = state

            return redirect(authorization_url)

        except Exception as e:
            logger.error(f'Google connect error: {e}', exc_info=True)
            flash('Failed to connect to Google Classroom. Please try again.', 'error')
            return redirect(url_for('main.profile', username=current_user.username))

    @bp.route('/google/callback')
    @login_required
    def google_callback():
        """Handle Google OAuth callback."""
        try:
            # Verify state
            state = session.get('google_auth_state')
            if not state or state != request.args.get('state'):
                flash('Invalid authentication state. Please try again.', 'error')
                return redirect(url_for('main.profile', username=current_user.username))

            # Exchange authorization code for tokens
            flow = get_google_flow()
            flow.fetch_token(authorization_response=request.url)

            credentials = flow.credentials

            # Store credentials in database
            current_user.google_access_token = credentials.token
            current_user.google_refresh_token = credentials.refresh_token
            current_user.google_token_expiry = credentials.expiry
            current_user.google_connected = True

            # Get Google user info
            try:
                service = build('oauth2', 'v2', credentials=credentials)
                user_info = service.userinfo().get().execute()
                current_user.google_id = user_info.get('id')
            except Exception as e:
                logger.warning(f'Could not fetch Google user info: {e}')

            db.session.commit()

            logger.info(f'User {current_user.username} connected Google Classroom')
            flash('Successfully connected to Google Classroom!', 'success')

        except Exception as e:
            logger.error(f'Google callback error: {e}', exc_info=True)
            flash('Failed to complete Google authentication. Please try again.', 'error')

        return redirect(url_for('main.profile', username=current_user.username))

    @bp.route('/google/disconnect', methods=['POST'])
    @login_required
    def google_disconnect():
        """Disconnect Google Classroom integration."""
        try:
            current_user.google_access_token = None
            current_user.google_refresh_token = None
            current_user.google_token_expiry = None
            current_user.google_id = None
            current_user.google_connected = False

            db.session.commit()

            logger.info(f'User {current_user.username} disconnected Google Classroom')
            flash('Google Classroom disconnected.', 'info')

        except Exception as e:
            logger.error(f'Google disconnect error: {e}', exc_info=True)
            flash('Failed to disconnect Google Classroom.', 'error')

        return redirect(url_for('main.profile', username=current_user.username))

    @bp.route('/api/google/courses')
    @login_required
    def api_google_courses():
        """Get user's Google Classroom courses."""
        try:
            if not current_user.google_connected:
                return jsonify({'success': False, 'error': 'Google Classroom not connected'}), 400

            creds = get_google_credentials()
            if not creds:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 400

            # Build Classroom API service
            service = build('classroom', 'v1', credentials=creds)

            # Get list of courses where user is a teacher
            results = service.courses().list(teacherId='me', courseStates=['ACTIVE']).execute()
            courses = results.get('courses', [])

            course_list = [{
                'id': course['id'],
                'name': course['name'],
                'section': course.get('section', ''),
                'descriptionHeading': course.get('descriptionHeading', ''),
                'room': course.get('room', ''),
                'enrollmentCode': course.get('enrollmentCode', '')
            } for course in courses]

            return jsonify({
                'success': True,
                'courses': course_list
            })

        except Exception as e:
            logger.error(f'Error fetching courses: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/google/share-resource', methods=['POST'])
    @login_required
    def api_share_to_classroom():
        """Share a resource to Google Classroom as an announcement."""
        try:
            if not current_user.google_connected:
                return jsonify({'success': False, 'error': 'Google Classroom not connected'}), 400

            data = request.get_json()
            course_id = data.get('course_id')
            resource_name = data.get('resource_name')
            resource_url = data.get('resource_url')
            resource_description = data.get('resource_description', '')

            if not all([course_id, resource_name, resource_url]):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400

            creds = get_google_credentials()
            if not creds:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 400

            # Build Classroom API service
            service = build('classroom', 'v1', credentials=creds)

            # Create announcement
            announcement = {
                'text': f'📚 New Resource: {resource_name}\n\n{resource_description}\n\n🔗 {resource_url}',
                'state': 'PUBLISHED'
            }

            result = service.courses().announcements().create(
                courseId=course_id,
                body=announcement
            ).execute()

            logger.info(f'User {current_user.username} shared resource to course {course_id}')

            return jsonify({
                'success': True,
                'message': 'Resource shared to Google Classroom!',
                'announcement_id': result.get('id')
            })

        except Exception as e:
            logger.error(f'Error sharing to classroom: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/google/create-material', methods=['POST'])
    @login_required
    def api_create_material():
        """Create a course material/assignment with the resource."""
        try:
            if not current_user.google_connected:
                return jsonify({'success': False, 'error': 'Google Classroom not connected'}), 400

            data = request.get_json()
            course_id = data.get('course_id')
            resource_name = data.get('resource_name')
            resource_url = data.get('resource_url')
            resource_description = data.get('resource_description', '')
            material_type = data.get('type', 'material')  # 'material' or 'assignment'

            if not all([course_id, resource_name, resource_url]):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400

            creds = get_google_credentials()
            if not creds:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 400

            # Build Classroom API service
            service = build('classroom', 'v1', credentials=creds)

            if material_type == 'material':
                # Create course work material
                material = {
                    'title': resource_name,
                    'description': resource_description,
                    'materials': [{
                        'link': {
                            'url': resource_url,
                            'title': resource_name
                        }
                    }],
                    'state': 'PUBLISHED'
                }

                result = service.courses().courseWorkMaterials().create(
                    courseId=course_id,
                    body=material
                ).execute()

                logger.info(f'User {current_user.username} created material in course {course_id}')

                return jsonify({
                    'success': True,
                    'message': 'Material added to Google Classroom!',
                    'material_id': result.get('id')
                })

            else:
                # Create assignment (would need more fields)
                return jsonify({'success': False, 'error': 'Assignment creation not yet implemented'}), 400

        except Exception as e:
            logger.error(f'Error creating material: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
