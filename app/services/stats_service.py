"""
Statistics Service - Calculates various statistics for resources.

This service handles all statistical calculations for resources and categories,
keeping business logic separate from routes.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class StatsService:
    """Service for calculating resource statistics."""

    @staticmethod
    def calculate_homepage_stats(categories: List[Dict]) -> Dict:
        """
        Calculate statistics for homepage display.

        Args:
            categories: List of all categories

        Returns:
            Dictionary with total_resources, total_categories, free_resources, subjects_covered
        """
        total_resources = sum(len(cat.get('resources', [])) for cat in categories)
        total_categories = len(categories)

        # Count free resources
        free_resources = 0
        for category in categories:
            for resource in category.get('resources', []):
                tags = [tag.lower() for tag in resource.get('tags', [])]
                if 'free' in tags:
                    free_resources += 1

        stats = {
            'total_resources': total_resources,
            'total_categories': total_categories,
            'free_resources': free_resources,
            'subjects_covered': 15  # Math, Science, ELA, Social Studies, etc.
        }

        logger.debug(f"Homepage stats: {stats}")
        return stats

    @staticmethod
    def calculate_category_stats(resources: List[Dict]) -> Dict:
        """
        Calculate detailed statistics for a category.

        Args:
            resources: List of resources in the category

        Returns:
            Dictionary with total, cost breakdown, and grade breakdown
        """
        total_resources = len(resources)

        # Count by cost
        free_count = StatsService._count_by_tag(
            resources,
            lambda tags: 'free' in tags and 'freemium' not in tags
        )
        freemium_count = StatsService._count_by_tag(
            resources,
            lambda tags: 'freemium' in tags
        )
        paid_count = StatsService._count_by_tag(
            resources,
            lambda tags: 'paid' in tags or 'premium' in tags
        )

        # Count by grade level
        grade_breakdown = {
            'Pre-K': StatsService._count_by_tag(
                resources,
                lambda tags: 'pre-k' in tags or 'prek' in tags
            ),
            'Elementary': StatsService._count_by_tag(
                resources,
                lambda tags: 'elementary' in tags or 'k-5' in tags
            ),
            'Middle School': StatsService._count_by_tag(
                resources,
                lambda tags: 'middle' in tags or '6-8' in tags
            ),
            'High School': StatsService._count_by_tag(
                resources,
                lambda tags: 'high school' in tags or '9-12' in tags
            ),
            'College': StatsService._count_by_tag(
                resources,
                lambda tags: 'college' in tags or 'higher ed' in tags
            ),
            'K-12': StatsService._count_by_tag(
                resources,
                lambda tags: 'k-12' in tags
            )
        }

        stats = {
            'total': total_resources,
            'free': free_count,
            'freemium': freemium_count,
            'paid': paid_count,
            'grade_breakdown': grade_breakdown
        }

        logger.debug(f"Category stats: total={total_resources}, free={free_count}")
        return stats

    @staticmethod
    def _count_by_tag(resources: List[Dict], condition_func) -> int:
        """
        Count resources matching a tag condition.

        Args:
            resources: List of resources
            condition_func: Function that takes normalized tags and returns bool

        Returns:
            Count of matching resources
        """
        count = 0
        for resource in resources:
            tags = [str(tag).lower() for tag in resource.get('tags', [])]
            if condition_func(tags):
                count += 1
        return count

    @staticmethod
    def get_related_categories(categories: List[Dict], current_category: Dict, count: int = 4) -> List[Dict]:
        """
        Find related categories (currently based on alphabetical proximity).

        Args:
            categories: List of all categories
            current_category: The current category
            count: Number of related categories to return

        Returns:
            List of related category dictionaries
        """
        try:
            current_index = categories.index(current_category)
        except ValueError:
            logger.warning("Current category not found in categories list")
            return []

        related = []

        # Get categories before and after (2 each)
        start = max(0, current_index - 2)
        end = min(len(categories), current_index + 3)

        for i in range(start, end):
            if i != current_index and categories[i] not in related:
                related.append({
                    'name': categories[i]['name'],
                    'icon': categories[i]['icon'],
                    'description': categories[i]['description'],
                    'count': len(categories[i].get('resources', []))
                })

        # Limit to requested count
        related = related[:count]

        logger.debug(f"Found {len(related)} related categories")
        return related

    @staticmethod
    def get_category_summary(categories: List[Dict], limit: int = 12) -> List[Dict]:
        """
        Get summary of categories for quick navigation.

        Args:
            categories: List of all categories
            limit: Maximum number of categories to return

        Returns:
            List of category summary dictionaries
        """
        summary = [
            {
                'name': cat['name'],
                'icon': cat['icon'],
                'description': cat['description'],
                'count': len(cat.get('resources', []))
            }
            for cat in categories[:limit]
        ]

        logger.debug(f"Generated summary for {len(summary)} categories")
        return summary
