"""
Resource Service - Data access layer for teaching resources.

This service handles all data loading, caching, and resource retrieval operations.
Implements enterprise-grade patterns including caching, error handling, and logging.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache
from flask import current_app

logger = logging.getLogger(__name__)


class ResourceService:
    """Service for managing teaching resources data."""

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_resources_data() -> Dict:
        """
        Load resources from JSON file with caching.

        Uses LRU cache to avoid repeated file I/O operations.
        Cache is automatically cleared when the process restarts.

        Returns:
            Dict containing categories and resources data

        Raises:
            FileNotFoundError: If resources.json is not found
            JSONDecodeError: If JSON is malformed
        """
        try:
            resources_file = Path(current_app.config['BASE_DIR']) / 'data' / 'resources.json'
            logger.info(f"Loading resources from {resources_file}")

            with open(resources_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"Successfully loaded {len(data.get('categories', []))} categories")
            return data

        except FileNotFoundError as e:
            logger.error(f"Resources file not found: {e}")
            return {'categories': []}

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in resources file: {e}")
            return {'categories': []}

        except Exception as e:
            logger.error(f"Unexpected error loading resources: {e}")
            return {'categories': []}

    @staticmethod
    def get_all_categories() -> List[Dict]:
        """
        Get all resource categories.

        Returns:
            List of category dictionaries
        """
        data = ResourceService._load_resources_data()
        return data.get('categories', [])

    @staticmethod
    def get_category_by_name(category_name: str) -> Optional[Dict]:
        """
        Find a category by name.

        Args:
            category_name: Name of the category to find

        Returns:
            Category dictionary if found, None otherwise
        """
        categories = ResourceService.get_all_categories()

        for category in categories:
            if category.get('name') == category_name:
                logger.debug(f"Found category: {category_name}")
                return category

        logger.warning(f"Category not found: {category_name}")
        return None

    @staticmethod
    def get_all_resources_flat() -> List[Dict]:
        """
        Get all resources flattened (for API/autocomplete).

        Returns:
            List of resource dictionaries with category info
        """
        categories = ResourceService.get_all_categories()
        all_resources = []

        for category in categories:
            for resource in category.get('resources', []):
                all_resources.append({
                    'name': resource.get('name'),
                    'description': resource.get('description'),
                    'category': category.get('name'),
                    'category_icon': category.get('icon'),
                    'tags': resource.get('tags', []),
                    'url': resource.get('url')
                })

        logger.debug(f"Flattened {len(all_resources)} resources")
        return all_resources

    @staticmethod
    def get_featured_resources(category_names: List[str], count: int = 6) -> List[Dict]:
        """
        Get featured resources from specified categories.

        Args:
            category_names: List of category names to pull from
            count: Maximum number of featured resources to return

        Returns:
            List of featured resource dictionaries with category info
        """
        categories = ResourceService.get_all_categories()
        featured = []

        for cat_name in category_names:
            if len(featured) >= count:
                break

            for category in categories:
                if category['name'] == cat_name and category.get('resources'):
                    resource = category['resources'][0].copy()
                    resource['category'] = category['name']
                    resource['category_icon'] = category['icon']
                    featured.append(resource)
                    break

        logger.debug(f"Selected {len(featured)} featured resources")
        return featured

    @staticmethod
    def validate_category_name(category_name: str) -> bool:
        """
        Validate that a category name exists.

        Args:
            category_name: Category name to validate

        Returns:
            True if category exists, False otherwise
        """
        if not category_name or not isinstance(category_name, str):
            return False

        # Check if category exists
        category = ResourceService.get_category_by_name(category_name)
        return category is not None

    @staticmethod
    def clear_cache():
        """Clear the resources data cache. Useful for testing or reloading data."""
        ResourceService._load_resources_data.cache_clear()
        logger.info("Resources cache cleared")
