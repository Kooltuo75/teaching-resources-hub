"""
Web routes for the Teaching Resources application.
"""
from flask import Blueprint, render_template, current_app, jsonify
import json
from pathlib import Path

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page - Ultimate Teacher Resource Directory."""
    # Load resources from JSON file
    resources_file = Path(current_app.config['BASE_DIR']) / 'data' / 'resources.json'

    try:
        with open(resources_file, 'r', encoding='utf-8') as f:
            resources_data = json.load(f)
    except FileNotFoundError:
        resources_data = {'categories': []}

    categories = resources_data.get('categories', [])

    # Calculate stats
    total_resources = sum(len(category.get('resources', [])) for category in categories)
    total_categories = len(categories)
    free_resources = 0

    # Count free resources
    for category in categories:
        for resource in category.get('resources', []):
            if 'free' in resource.get('tags', []):
                free_resources += 1

    # Get featured resources (first resource from select categories)
    featured_resources = []
    featured_categories = ['Educational Websites & Portals', 'Assessment & Testing Tools',
                          'Learning Management Systems', 'Mathematics Resources',
                          'Computer Science & Coding', 'Video & Multimedia Creation']

    for cat_name in featured_categories:
        for category in categories:
            if category['name'] == cat_name and category.get('resources'):
                resource = category['resources'][0].copy()
                resource['category'] = category['name']
                resource['category_icon'] = category['icon']
                featured_resources.append(resource)
                break

    # Prepare category summary for quick navigation
    category_summary = [
        {
            'name': cat['name'],
            'icon': cat['icon'],
            'description': cat['description'],
            'count': len(cat.get('resources', []))
        }
        for cat in categories[:12]  # Show first 12 categories on homepage
    ]

    stats = {
        'total_resources': total_resources,
        'total_categories': total_categories,
        'free_resources': free_resources,
        'subjects_covered': 15  # Math, Science, ELA, Social Studies, Arts, Music, PE, Languages, CS, etc.
    }

    return render_template('index.html',
                         app_name=current_app.config['APP_NAME'],
                         stats=stats,
                         featured_resources=featured_resources,
                         categories=category_summary)

@bp.route('/about')
def about():
    """About page with project information."""
    return render_template('base.html',
                         app_name=current_app.config['APP_NAME'],
                         content='<h2>About</h2><p>Teaching Resources Hub - Supporting educators with comprehensive tools and resources.</p>')

@bp.route('/resources')
def resources():
    """Teaching resources directory with searchable categories."""
    # Load resources from JSON file
    resources_file = Path(current_app.config['BASE_DIR']) / 'data' / 'resources.json'

    try:
        with open(resources_file, 'r', encoding='utf-8') as f:
            resources_data = json.load(f)
    except FileNotFoundError:
        resources_data = {'categories': []}

    # Calculate total resources count
    categories = resources_data.get('categories', [])
    total_resources = sum(len(category.get('resources', [])) for category in categories)

    return render_template('resources.html',
                         app_name=current_app.config['APP_NAME'],
                         categories=categories,
                         total_resources=total_resources)

@bp.route('/category/<category_name>')
def category_detail(category_name):
    """Detail page for a specific category."""
    # Load resources from JSON file
    resources_file = Path(current_app.config['BASE_DIR']) / 'data' / 'resources.json'

    try:
        with open(resources_file, 'r', encoding='utf-8') as f:
            resources_data = json.load(f)
    except FileNotFoundError:
        resources_data = {'categories': []}

    categories = resources_data.get('categories', [])

    # Find the requested category
    current_category = None
    for cat in categories:
        if cat['name'] == category_name:
            current_category = cat
            break

    if not current_category:
        # Category not found, redirect to resources page
        from flask import redirect, url_for
        return redirect(url_for('main.resources'))

    # Calculate category statistics
    resources = current_category.get('resources', [])
    total_resources = len(resources)

    # Count by cost
    free_count = sum(1 for r in resources if any('free' in str(tag).lower() and 'freemium' not in str(tag).lower() for tag in r.get('tags', [])))
    freemium_count = sum(1 for r in resources if any('freemium' in str(tag).lower() for tag in r.get('tags', [])))
    paid_count = sum(1 for r in resources if any('paid' in str(tag).lower() or 'premium' in str(tag).lower() for tag in r.get('tags', [])))

    # Count by grade level
    grade_breakdown = {
        'Pre-K': sum(1 for r in resources if any('pre-k' in str(tag).lower() or 'prek' in str(tag).lower() for tag in r.get('tags', []))),
        'Elementary': sum(1 for r in resources if any('elementary' in str(tag).lower() or 'k-5' in str(tag).lower() for tag in r.get('tags', []))),
        'Middle School': sum(1 for r in resources if any('middle' in str(tag).lower() or '6-8' in str(tag).lower() for tag in r.get('tags', []))),
        'High School': sum(1 for r in resources if any('high school' in str(tag).lower() or '9-12' in str(tag).lower() for tag in r.get('tags', []))),
        'College': sum(1 for r in resources if any('college' in str(tag).lower() or 'higher ed' in str(tag).lower() for tag in r.get('tags', []))),
        'K-12': sum(1 for r in resources if any('k-12' in str(tag).lower() for tag in r.get('tags', [])))
    }

    stats = {
        'total': total_resources,
        'free': free_count,
        'freemium': freemium_count,
        'paid': paid_count,
        'grade_breakdown': grade_breakdown
    }

    # Find related categories (alphabetically adjacent + same subject area)
    current_index = categories.index(current_category)
    related_categories = []

    # Get 2 categories before and after
    for i in range(max(0, current_index - 2), min(len(categories), current_index + 3)):
        if i != current_index and categories[i] not in related_categories:
            related_categories.append({
                'name': categories[i]['name'],
                'icon': categories[i]['icon'],
                'description': categories[i]['description'],
                'count': len(categories[i].get('resources', []))
            })

    # Limit to 4 related categories
    related_categories = related_categories[:4]

    return render_template('category_detail.html',
                         app_name=current_app.config['APP_NAME'],
                         category=current_category,
                         stats=stats,
                         related_categories=related_categories,
                         total_categories=len(categories))

@bp.route('/api/resources')
def api_resources():
    """API endpoint to get all resources as JSON for autocomplete."""
    # Load resources from JSON file
    resources_file = Path(current_app.config['BASE_DIR']) / 'data' / 'resources.json'

    try:
        with open(resources_file, 'r', encoding='utf-8') as f:
            resources_data = json.load(f)
    except FileNotFoundError:
        return jsonify({'categories': []})

    # Flatten resources for easier searching
    all_resources = []
    for category in resources_data.get('categories', []):
        for resource in category.get('resources', []):
            all_resources.append({
                'name': resource.get('name'),
                'description': resource.get('description'),
                'category': category.get('name'),
                'category_icon': category.get('icon'),
                'tags': resource.get('tags', []),
                'url': resource.get('url')
            })

    return jsonify({'resources': all_resources})
