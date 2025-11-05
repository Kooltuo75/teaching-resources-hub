"""
REST API routes for external integrations and tools.
Provides programmatic access to resources, categories, and user data.
"""

from flask import jsonify, request, send_file, Response, current_app
from flask_login import login_required, current_user
from app.models import db, User, Favorite
from app.services.resource_service import ResourceService
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import logging
import json
import io

logger = logging.getLogger(__name__)


def register_api_routes(bp):
    """Register API routes to the blueprint."""

    # ===========================================
    # PUBLIC API ENDPOINTS (No auth required)
    # ===========================================

    @bp.route('/api/v1/resources', methods=['GET'])
    def api_get_resources():
        """
        Get all resources with optional filtering.

        Query parameters:
        - category: Filter by category name
        - grade: Filter by grade level
        - subject: Filter by subject
        - cost: Filter by cost (free, freemium, paid)
        - search: Search in name and description
        - limit: Limit number of results (default: all)
        - offset: Skip first N results (default: 0)
        """
        try:
            resource_service = ResourceService()
            all_resources = resource_service.get_all_resources_flat()

            # Apply filters
            category_filter = request.args.get('category')
            grade_filter = request.args.get('grade')
            subject_filter = request.args.get('subject')
            cost_filter = request.args.get('cost')
            search_query = request.args.get('search', '').lower()

            filtered = all_resources

            if category_filter:
                filtered = [r for r in filtered if r.get('category') == category_filter]

            if grade_filter:
                filtered = [r for r in filtered if grade_filter.lower() in r.get('grades', '').lower()]

            if subject_filter:
                filtered = [r for r in filtered if subject_filter.lower() in r.get('subject', '').lower()]

            if cost_filter:
                filtered = [r for r in filtered if cost_filter.lower() in r.get('cost', '').lower()]

            if search_query:
                filtered = [r for r in filtered if
                           search_query in r.get('name', '').lower() or
                           search_query in r.get('description', '').lower()]

            # Pagination
            limit = int(request.args.get('limit', len(filtered)))
            offset = int(request.args.get('offset', 0))

            paginated = filtered[offset:offset + limit]

            return jsonify({
                'success': True,
                'total': len(filtered),
                'count': len(paginated),
                'offset': offset,
                'limit': limit,
                'resources': paginated
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/v1/categories', methods=['GET'])
    def api_get_categories():
        """
        Get all categories with resource counts.

        Query parameters:
        - include_resources: Include full resource data (default: false)
        """
        try:
            resource_service = ResourceService()
            categories = resource_service.get_all_categories()

            include_resources = request.args.get('include_resources', 'false').lower() == 'true'

            if not include_resources:
                # Return just category metadata without full resources
                categories = [{
                    'name': cat['name'],
                    'description': cat.get('description', ''),
                    'icon': cat.get('icon', '📚'),
                    'resource_count': len(cat.get('resources', []))
                } for cat in categories]

            return jsonify({
                'success': True,
                'count': len(categories),
                'categories': categories
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/v1/categories/<category_name>', methods=['GET'])
    def api_get_category(category_name):
        """Get a specific category with all its resources."""
        try:
            resource_service = ResourceService()
            category = resource_service.get_category_by_name(category_name)

            if not category:
                return jsonify({'success': False, 'error': 'Category not found'}), 404

            return jsonify({
                'success': True,
                'category': category
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/v1/resources/<resource_id>', methods=['GET'])
    def api_get_resource(resource_id):
        """Get a specific resource by ID."""
        try:
            resource_service = ResourceService()
            all_resources = resource_service.get_all_resources_flat()

            resource = next((r for r in all_resources if r['id'] == resource_id), None)

            if not resource:
                return jsonify({'success': False, 'error': 'Resource not found'}), 404

            # Add favorite count if available
            favorite_count = Favorite.query.filter_by(resource_id=resource_id).count()
            resource['favorite_count'] = favorite_count

            return jsonify({
                'success': True,
                'resource': resource
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/v1/stats', methods=['GET'])
    def api_get_stats():
        """Get platform statistics."""
        try:
            resource_service = ResourceService()
            categories = resource_service.get_all_categories()
            all_resources = resource_service.get_all_resources()

            # Calculate stats
            total_resources = len(all_resources)
            total_categories = len(categories)
            total_users = User.query.count()
            total_favorites = Favorite.query.count()

            # Top categories by resource count
            top_categories = sorted(
                [{'name': cat['name'], 'count': len(cat.get('resources', []))}
                 for cat in categories],
                key=lambda x: x['count'],
                reverse=True
            )[:10]

            # Most favorited resources
            from sqlalchemy import func
            most_favorited = db.session.query(
                Favorite.resource_id,
                func.count(Favorite.id).label('count')
            ).group_by(Favorite.resource_id).order_by(
                func.count(Favorite.id).desc()
            ).limit(10).all()

            most_favorited_resources = []
            for fav in most_favorited:
                resource = next((r for r in all_resources if r['id'] == fav.resource_id), None)
                if resource:
                    most_favorited_resources.append({
                        'resource': resource,
                        'favorite_count': fav.count
                    })

            return jsonify({
                'success': True,
                'stats': {
                    'total_resources': total_resources,
                    'total_categories': total_categories,
                    'total_users': total_users,
                    'total_favorites': total_favorites,
                    'top_categories': top_categories,
                    'most_favorited': most_favorited_resources
                }
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/v1/search', methods=['GET'])
    def api_search():
        """
        Search resources with advanced options.

        Query parameters:
        - q: Search query (required)
        - fields: Comma-separated fields to search (name,description,tags)
        - limit: Max results (default: 50)
        """
        try:
            query = request.args.get('q', '').lower()
            if not query:
                return jsonify({'success': False, 'error': 'Query parameter "q" required'}), 400

            fields = request.args.get('fields', 'name,description,tags').split(',')
            limit = int(request.args.get('limit', 50))

            resource_service = ResourceService()
            all_resources = resource_service.get_all_resources()

            results = []
            for resource in all_resources:
                score = 0

                if 'name' in fields and query in resource.get('name', '').lower():
                    score += 3

                if 'description' in fields and query in resource.get('description', '').lower():
                    score += 2

                if 'tags' in fields:
                    for tag in resource.get('tags', []):
                        if query in tag.lower():
                            score += 1

                if score > 0:
                    results.append({
                        'resource': resource,
                        'relevance_score': score
                    })

            # Sort by relevance
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            results = results[:limit]

            return jsonify({
                'success': True,
                'query': query,
                'count': len(results),
                'results': results
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===========================================
    # AUTHENTICATED API ENDPOINTS
    # ===========================================

    @bp.route('/api/v1/user/favorites', methods=['GET'])
    @login_required
    def api_get_user_favorites():
        """Get current user's favorites."""
        try:
            favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(
                Favorite.added_at.desc()
            ).all()

            resource_service = ResourceService()
            all_resources = resource_service.get_all_resources()
            resources_dict = {r['id']: r for r in all_resources}

            favorite_list = []
            for fav in favorites:
                if fav.resource_id in resources_dict:
                    resource = resources_dict[fav.resource_id].copy()
                    resource['favorited_at'] = fav.added_at.isoformat()
                    resource['user_note'] = fav.notes
                    favorite_list.append(resource)

            return jsonify({
                'success': True,
                'count': len(favorite_list),
                'favorites': favorite_list
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/v1/user/favorites/export', methods=['GET'])
    @login_required
    def api_export_favorites():
        """
        Export user's favorites in various formats.

        Query parameters:
        - format: json, csv, or txt (default: json)
        """
        try:
            export_format = request.args.get('format', 'json').lower()

            favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(
                Favorite.added_at.desc()
            ).all()

            resource_service = ResourceService()
            all_resources = resource_service.get_all_resources()
            resources_dict = {r['id']: r for r in all_resources}

            favorite_list = []
            for fav in favorites:
                if fav.resource_id in resources_dict:
                    resource = resources_dict[fav.resource_id].copy()
                    resource['favorited_at'] = fav.added_at.isoformat()
                    resource['user_note'] = fav.notes
                    favorite_list.append(resource)

            if export_format == 'json':
                output = json.dumps({'favorites': favorite_list}, indent=2)
                mimetype = 'application/json'
                filename = f'favorites_{datetime.now().strftime("%Y%m%d")}.json'

            elif export_format == 'csv':
                import csv
                output_io = io.StringIO()
                writer = csv.writer(output_io)

                # Header
                writer.writerow(['Name', 'Description', 'URL', 'Category', 'Cost', 'Grades', 'My Note', 'Added Date'])

                # Data
                for resource in favorite_list:
                    writer.writerow([
                        resource.get('name', ''),
                        resource.get('description', ''),
                        resource.get('url', ''),
                        resource.get('category', ''),
                        resource.get('cost', ''),
                        resource.get('grades', ''),
                        resource.get('user_note', ''),
                        resource.get('favorited_at', '')
                    ])

                output = output_io.getvalue()
                mimetype = 'text/csv'
                filename = f'favorites_{datetime.now().strftime("%Y%m%d")}.csv'

            elif export_format == 'txt':
                lines = [f"My Favorite Teaching Resources - {datetime.now().strftime('%B %d, %Y')}\n"]
                lines.append("=" * 80 + "\n\n")

                for resource in favorite_list:
                    lines.append(f"📌 {resource.get('name', '')}\n")
                    lines.append(f"   {resource.get('description', '')}\n")
                    lines.append(f"   🔗 {resource.get('url', '')}\n")
                    lines.append(f"   📂 {resource.get('category', '')}\n")
                    if resource.get('user_note'):
                        lines.append(f"   💭 Note: {resource.get('user_note')}\n")
                    lines.append("\n")

                output = ''.join(lines)
                mimetype = 'text/plain'
                filename = f'favorites_{datetime.now().strftime("%Y%m%d")}.txt'

            else:
                return jsonify({'success': False, 'error': 'Invalid format. Use json, csv, or txt'}), 400

            # Create file response
            output_bytes = io.BytesIO(output.encode('utf-8'))
            output_bytes.seek(0)

            return send_file(
                output_bytes,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @bp.route('/api/v1/user/profile', methods=['GET'])
    @login_required
    def api_get_user_profile():
        """Get current user's profile information."""
        try:
            profile_data = {
                'username': current_user.username,
                'display_name': current_user.display_name,
                'email': current_user.email,
                'bio': current_user.bio,
                'school': current_user.school,
                'grade_levels': current_user.grade_levels,
                'subjects': current_user.subjects,
                'teaching_philosophy': current_user.teaching_philosophy,
                'website_url': current_user.website_url,
                'twitter_handle': current_user.twitter_handle,
                'created_at': current_user.created_at.isoformat(),
                'theme': {
                    'background_color': current_user.background_color,
                    'text_color': current_user.text_color,
                    'accent_color': current_user.accent_color,
                    'profile_theme': current_user.profile_theme
                }
            }

            return jsonify({
                'success': True,
                'profile': profile_data
            })

        except Exception as e:
            logger.error(f'API error: {e}', exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    # ===========================================
    # RSS & CALENDAR FEEDS
    # ===========================================

    @bp.route('/feed/rss', methods=['GET'])
    def rss_feed():
        """RSS feed for resources (latest additions and updates)."""
        try:
            resource_service = ResourceService()
            all_resources = resource_service.get_all_resources_flat()

            # Get latest 50 resources
            latest_resources = all_resources[:50]

            # Build RSS XML
            rss = Element('rss', version='2.0')
            channel = SubElement(rss, 'channel')

            SubElement(channel, 'title').text = current_app.config['APP_NAME']
            SubElement(channel, 'link').text = request.url_root
            SubElement(channel, 'description').text = 'Latest teaching resources and educational tools'
            SubElement(channel, 'language').text = 'en-us'
            SubElement(channel, 'lastBuildDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

            for resource in latest_resources:
                item = SubElement(channel, 'item')
                SubElement(item, 'title').text = resource.get('name', '')
                SubElement(item, 'link').text = resource.get('url', '')
                SubElement(item, 'description').text = resource.get('description', '')
                SubElement(item, 'category').text = resource.get('category', '')
                SubElement(item, 'guid').text = resource.get('url', '')

            xml_string = tostring(rss, encoding='unicode', method='xml')
            xml_pretty = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string

            return Response(xml_pretty, mimetype='application/rss+xml')

        except Exception as e:
            logger.error(f'RSS feed error: {e}', exc_info=True)
            return Response('Error generating RSS feed', status=500)

    @bp.route('/feed/favorites.ics', methods=['GET'])
    @login_required
    def ical_favorites():
        """iCal/Calendar export of user's favorited resources."""
        try:
            favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(
                Favorite.added_at.desc()
            ).all()

            resource_service = ResourceService()
            all_resources = resource_service.get_all_resources()
            resources_dict = {r['id']: r for r in all_resources}

            # Build iCal format
            ical_lines = [
                'BEGIN:VCALENDAR',
                'VERSION:2.0',
                f'PRODID:-//{current_app.config["APP_NAME"]}//EN',
                'CALSCALE:GREGORIAN',
                'METHOD:PUBLISH',
                f'X-WR-CALNAME:My Favorite Teaching Resources',
                'X-WR-TIMEZONE:UTC',
                'X-WR-CALDESC:Favorited teaching resources from Teaching Resources Hub'
            ]

            for fav in favorites:
                if fav.resource_id in resources_dict:
                    resource = resources_dict[fav.resource_id]

                    # Create a VTODO (to-do item) for each resource
                    dtstart = fav.added_at.strftime('%Y%m%dT%H%M%SZ')
                    uid = f'{fav.resource_id}@teachinghub.local'

                    ical_lines.extend([
                        'BEGIN:VTODO',
                        f'UID:{uid}',
                        f'DTSTAMP:{dtstart}',
                        f'SUMMARY:{resource.get("name", "")}',
                        f'DESCRIPTION:{resource.get("description", "")}\\n\\nURL: {resource.get("url", "")}',
                        f'URL:{resource.get("url", "")}',
                        f'CATEGORIES:{resource.get("category", "")}',
                        'STATUS:NEEDS-ACTION',
                        'PRIORITY:5',
                        'END:VTODO'
                    ])

            ical_lines.append('END:VCALENDAR')

            ical_content = '\r\n'.join(ical_lines)

            return Response(
                ical_content,
                mimetype='text/calendar',
                headers={'Content-Disposition': 'attachment; filename=favorites.ics'}
            )

        except Exception as e:
            logger.error(f'iCal export error: {e}', exc_info=True)
            return Response('Error generating calendar file', status=500)
