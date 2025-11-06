"""
Analytics Service - Track user behavior and generate insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import request, session
from flask_login import current_user
from sqlalchemy import func, desc
from app.models import (
    db, ResourceView, SearchQuery, CategoryView, PageView,
    Review, ResourceSubmission, User, Follow
)

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for tracking analytics and generating insights."""

    @staticmethod
    def get_session_id() -> str:
        """Get or create a session ID for tracking."""
        if 'analytics_session_id' not in session:
            import uuid
            session['analytics_session_id'] = str(uuid.uuid4())
        return session['analytics_session_id']

    @staticmethod
    def get_user_id() -> Optional[int]:
        """Get current user ID if authenticated."""
        return current_user.id if current_user.is_authenticated else None

    @staticmethod
    def get_ip_address() -> str:
        """Get user's IP address."""
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
        return request.environ.get('REMOTE_ADDR', 'unknown')

    @staticmethod
    def track_resource_view(resource_name: str, resource_category: str, resource_url: str):
        """Track a resource view."""
        try:
            view = ResourceView(
                resource_name=resource_name,
                resource_category=resource_category,
                resource_url=resource_url,
                user_id=AnalyticsService.get_user_id(),
                ip_address=AnalyticsService.get_ip_address(),
                user_agent=request.user_agent.string[:500] if request.user_agent else None,
                session_id=AnalyticsService.get_session_id(),
                referrer=request.referrer[:500] if request.referrer else None
            )
            db.session.add(view)
            db.session.commit()
            logger.debug(f"Tracked resource view: {resource_name}")
        except Exception as e:
            logger.error(f"Error tracking resource view: {e}")
            db.session.rollback()

    @staticmethod
    def track_search(query: str, results_count: int, category_filter: Optional[str] = None):
        """Track a search query."""
        try:
            search = SearchQuery(
                query=query[:500],
                results_count=results_count,
                user_id=AnalyticsService.get_user_id(),
                ip_address=AnalyticsService.get_ip_address(),
                session_id=AnalyticsService.get_session_id(),
                category_filter=category_filter,
                had_results=(results_count > 0)
            )
            db.session.add(search)
            db.session.commit()
            logger.debug(f"Tracked search: {query}")
        except Exception as e:
            logger.error(f"Error tracking search: {e}")
            db.session.rollback()

    @staticmethod
    def track_category_view(category_name: str):
        """Track a category view."""
        try:
            view = CategoryView(
                category_name=category_name,
                user_id=AnalyticsService.get_user_id(),
                ip_address=AnalyticsService.get_ip_address(),
                session_id=AnalyticsService.get_session_id()
            )
            db.session.add(view)
            db.session.commit()
            logger.debug(f"Tracked category view: {category_name}")
        except Exception as e:
            logger.error(f"Error tracking category view: {e}")
            db.session.rollback()

    @staticmethod
    def track_page_view(path: str, method: str, status_code: int, response_time: float):
        """Track a page view."""
        try:
            view = PageView(
                path=path[:500],
                method=method,
                status_code=status_code,
                response_time=response_time,
                user_id=AnalyticsService.get_user_id(),
                ip_address=AnalyticsService.get_ip_address(),
                user_agent=request.user_agent.string[:500] if request.user_agent else None,
                session_id=AnalyticsService.get_session_id(),
                referrer=request.referrer[:500] if request.referrer else None
            )
            db.session.add(view)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")
            db.session.rollback()

    # Analytics Dashboard Methods

    @staticmethod
    def get_top_resources(days: int = 7, limit: int = 10) -> List[Dict]:
        """Get most viewed resources."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            results = db.session.query(
                ResourceView.resource_name,
                ResourceView.resource_category,
                func.count(ResourceView.id).label('view_count')
            ).filter(
                ResourceView.viewed_at >= cutoff
            ).group_by(
                ResourceView.resource_name,
                ResourceView.resource_category
            ).order_by(
                desc('view_count')
            ).limit(limit).all()

            return [
                {
                    'name': r.resource_name,
                    'category': r.resource_category,
                    'views': r.view_count
                }
                for r in results
            ]
        except Exception as e:
            logger.debug(f"Could not load top resources: {e}")
            return []

    @staticmethod
    def get_top_categories(days: int = 7, limit: int = 10) -> List[Dict]:
        """Get most viewed categories."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            results = db.session.query(
                CategoryView.category_name,
                func.count(CategoryView.id).label('view_count')
            ).filter(
                CategoryView.viewed_at >= cutoff
            ).group_by(
                CategoryView.category_name
            ).order_by(
                desc('view_count')
            ).limit(limit).all()

            return [
                {
                    'name': r.category_name,
                    'views': r.view_count
                }
                for r in results
            ]
        except Exception as e:
            logger.debug(f"Could not load top categories: {e}")
            return []

    @staticmethod
    def get_top_searches(days: int = 7, limit: int = 10) -> List[Dict]:
        """Get most popular search queries."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            results = db.session.query(
                SearchQuery.query,
                func.count(SearchQuery.id).label('search_count'),
                func.avg(SearchQuery.results_count).label('avg_results')
            ).filter(
                SearchQuery.searched_at >= cutoff
            ).group_by(
                SearchQuery.query
            ).order_by(
                desc('search_count')
            ).limit(limit).all()

            return [
                {
                    'query': r.query,
                    'count': r.search_count,
                    'avg_results': round(r.avg_results or 0, 1)
                }
                for r in results
            ]
        except Exception as e:
            logger.debug(f"Could not load top searches: {e}")
            return []

    @staticmethod
    def get_site_statistics(days: int = 7) -> Dict:
        """Get overall site statistics."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Page views
            total_page_views = PageView.query.filter(PageView.viewed_at >= cutoff).count()

            # Unique sessions
            unique_sessions = db.session.query(
                func.count(func.distinct(PageView.session_id))
            ).filter(PageView.viewed_at >= cutoff).scalar()

            # Resource views
            total_resource_views = ResourceView.query.filter(ResourceView.viewed_at >= cutoff).count()

            # Searches
            total_searches = SearchQuery.query.filter(SearchQuery.searched_at >= cutoff).count()

            # New users
            new_users = User.query.filter(User.created_at >= cutoff).count()

            # New reviews
            new_reviews = Review.query.filter(Review.created_at >= cutoff).count()

            # New submissions
            new_submissions = ResourceSubmission.query.filter(ResourceSubmission.created_at >= cutoff).count()

            # Average response time
            avg_response_time = db.session.query(
                func.avg(PageView.response_time)
            ).filter(PageView.viewed_at >= cutoff).scalar()

            return {
                'total_page_views': total_page_views,
                'unique_sessions': unique_sessions or 0,
                'total_resource_views': total_resource_views,
                'total_searches': total_searches,
                'new_users': new_users,
                'new_reviews': new_reviews,
                'new_submissions': new_submissions,
                'avg_response_time': round(avg_response_time or 0, 3)
            }
        except Exception as e:
            logger.debug(f"Could not load site statistics: {e}")
            return {
                'total_page_views': 0,
                'unique_sessions': 0,
                'total_resource_views': 0,
                'total_searches': 0,
                'new_users': 0,
                'new_reviews': 0,
                'new_submissions': 0,
                'avg_response_time': 0
            }

    @staticmethod
    def get_daily_activity(days: int = 7) -> List[Dict]:
        """Get daily activity breakdown."""
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Use PostgreSQL date_trunc or SQLite date() depending on database
            from sqlalchemy.sql import func

            results = db.session.query(
                func.date(PageView.viewed_at).label('date'),
                func.count(PageView.id).label('views')
            ).filter(
                PageView.viewed_at >= cutoff
            ).group_by(
                func.date(PageView.viewed_at)
            ).order_by('date').all()

            return [
                {
                    'date': r.date.strftime('%Y-%m-%d') if hasattr(r.date, 'strftime') else str(r.date),
                    'views': r.views
                }
                for r in results
            ]
        except Exception as e:
            logger.debug(f"Could not load daily activity: {e}")
            return []
