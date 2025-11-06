"""
Database Models for Teaching Resources Hub

Includes User, Favorite, and profile customization models.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model with MySpace-style profile customization."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile Information
    display_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    school = db.Column(db.String(200))
    grade_level = db.Column(db.String(50))  # e.g., "Elementary", "Middle School", etc.
    subjects_taught = db.Column(db.String(200))  # Comma-separated subjects
    years_teaching = db.Column(db.Integer)
    location = db.Column(db.String(100))  # City, State
    website = db.Column(db.String(200))
    twitter_handle = db.Column(db.String(50))  # Twitter username (without @)

    # MySpace-Style Customization
    profile_picture = db.Column(db.String(500))  # URL or path
    background_color = db.Column(db.String(7), default='#ffffff')  # Hex color
    text_color = db.Column(db.String(7), default='#333333')
    accent_color = db.Column(db.String(7), default='#667eea')  # For buttons, links
    profile_theme = db.Column(db.String(20), default='light')  # light, dark, colorful
    favorite_quote = db.Column(db.String(500))

    # Custom Sections (like MySpace "About Me", "Who I'd Like to Meet")
    about_me = db.Column(db.Text)
    teaching_philosophy = db.Column(db.Text)
    favorite_lesson = db.Column(db.Text)
    classroom_setup = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Privacy Settings
    profile_public = db.Column(db.Boolean, default=True)
    show_favorites_public = db.Column(db.Boolean, default=True)

    # Collaboration Board (Phase 2)
    looking_for = db.Column(db.Text)  # What help/collaboration they need
    can_help_with = db.Column(db.Text)  # What expertise they can offer
    open_to_collaboration = db.Column(db.Boolean, default=True)  # Toggle for collaboration requests

    # Google Classroom Integration
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google account ID
    google_access_token = db.Column(db.Text, nullable=True)  # Encrypted access token
    google_refresh_token = db.Column(db.Text, nullable=True)  # Encrypted refresh token
    google_token_expiry = db.Column(db.DateTime, nullable=True)  # Token expiration time
    google_connected = db.Column(db.Boolean, default=False)  # Is Google Classroom connected?

    # Reputation & Gamification
    reputation_score = db.Column(db.Integer, default=0)  # Points earned from contributions
    total_reviews = db.Column(db.Integer, default=0)  # Number of reviews written
    total_submissions = db.Column(db.Integer, default=0)  # Number of resources submitted
    helpful_votes_received = db.Column(db.Integer, default=0)  # Helpful votes on their reviews

    # Moderation
    is_moderator = db.Column(db.Boolean, default=False)
    is_verified_teacher = db.Column(db.Boolean, default=False)

    # Relationships
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    submitted_resources = db.relationship('ResourceSubmission',
                                         foreign_keys='ResourceSubmission.user_id',
                                         backref='submitter',
                                         lazy='dynamic',
                                         cascade='all, delete-orphan')

    # Social relationships
    following = db.relationship(
        'Follow',
        foreign_keys='Follow.follower_id',
        backref='follower',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys='Follow.followed_id',
        backref='followed',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    activities = db.relationship('Activity',
                                 foreign_keys='Activity.user_id',
                                 backref='user',
                                 lazy='dynamic',
                                 cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def get_profile_url(self):
        """Get the URL to this user's profile."""
        return f'/profile/{self.username}'

    def follow(self, user):
        """Follow another user."""
        if not self.is_following(user):
            follow = Follow(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)
            return follow

    def unfollow(self, user):
        """Unfollow a user."""
        follow = self.following.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            return True
        return False

    def is_following(self, user):
        """Check if this user is following another user."""
        return self.following.filter_by(followed_id=user.id).first() is not None

    def get_follower_count(self):
        """Get the number of followers."""
        return self.followers.count()

    def get_following_count(self):
        """Get the number of users this user is following."""
        return self.following.count()

    def __repr__(self):
        return f'<User {self.username}>'


class Favorite(db.Model):
    """Favorite/bookmarked resources for users."""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Resource Information (denormalized for faster access)
    resource_name = db.Column(db.String(200), nullable=False)
    resource_category = db.Column(db.String(100), nullable=False)
    resource_url = db.Column(db.String(500), nullable=False)
    resource_description = db.Column(db.Text)
    resource_tags = db.Column(db.String(500))  # Comma-separated

    # Personal Notes
    personal_note = db.Column(db.Text)  # User's notes about this resource
    personal_rating = db.Column(db.Integer)  # 1-5 stars

    # Usage tracking
    times_used = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Organization
    folder = db.Column(db.String(100))  # Optional folder/collection name

    def __repr__(self):
        return f'<Favorite {self.resource_name} by User {self.user_id}>'


class ProfileVisit(db.Model):
    """Track profile visits for analytics."""

    __tablename__ = 'profile_visits'

    id = db.Column(db.Integer, primary_key=True)
    profile_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    visitor_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # None if not logged in
    visitor_ip = db.Column(db.String(45))  # IPv4 or IPv6
    visited_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<ProfileVisit profile={self.profile_user_id} at {self.visited_at}>'


class Review(db.Model):
    """Resource reviews and ratings by teachers."""

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Resource Information (denormalized for performance)
    resource_name = db.Column(db.String(200), nullable=False, index=True)
    resource_category = db.Column(db.String(100), nullable=False)
    resource_url = db.Column(db.String(500), nullable=False)

    # Review Content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))  # Optional review title
    review_text = db.Column(db.Text, nullable=False)  # The actual review

    # Context about usage
    grade_level_used = db.Column(db.String(50))  # What grade level they used it with
    subject_used = db.Column(db.String(100))  # What subject
    time_used = db.Column(db.String(50))  # "Less than 1 month", "1-6 months", etc.

    # Engagement
    helpful_votes = db.Column(db.Integer, default=0)  # Number of "helpful" votes
    reported = db.Column(db.Boolean, default=False)  # Flagged for moderation
    verified_purchase = db.Column(db.Boolean, default=False)  # If applicable

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Review of {self.resource_name} by User {self.user_id}>'


class ReviewHelpful(db.Model):
    """Track which users found which reviews helpful."""

    __tablename__ = 'review_helpful'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure a user can only vote once per review
    __table_args__ = (db.UniqueConstraint('review_id', 'user_id', name='unique_review_helpful'),)

    def __repr__(self):
        return f'<ReviewHelpful review={self.review_id} user={self.user_id}>'


class ResourceSubmission(db.Model):
    """User-submitted resources pending approval."""

    __tablename__ = 'resource_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Resource Details
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)

    # Additional metadata
    suggested_grade_levels = db.Column(db.String(200))  # Comma-separated
    tags = db.Column(db.String(500))  # Comma-separated tags
    cost = db.Column(db.String(50))  # "Free", "Freemium", "Paid", etc.
    why_useful = db.Column(db.Text)  # Why the submitter thinks it's useful

    # Approval Workflow
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)  # If rejected, why?

    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ResourceSubmission {self.name} by User {self.user_id} - {self.status}>'


class Follow(db.Model):
    """User following relationships."""

    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Ensure a user can't follow the same person twice
    __table_args__ = (db.UniqueConstraint('follower_id', 'followed_id', name='unique_follow'),)

    def __repr__(self):
        return f'<Follow {self.follower_id} -> {self.followed_id}>'


class Activity(db.Model):
    """Activity feed for social features."""

    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # Activity Details
    activity_type = db.Column(db.String(50), nullable=False)  # review, favorite, submission, follow
    activity_data = db.Column(db.Text)  # JSON data about the activity

    # Related Objects (polymorphic)
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For follows
    related_resource_name = db.Column(db.String(200))  # For reviews, favorites
    related_resource_url = db.Column(db.String(500))

    # Visibility
    is_public = db.Column(db.Boolean, default=True)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Activity {self.activity_type} by User {self.user_id} at {self.created_at}>'


class ResourceView(db.Model):
    """Track resource views for analytics."""

    __tablename__ = 'resource_views'

    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(200), nullable=False, index=True)
    resource_category = db.Column(db.String(100), index=True)
    resource_url = db.Column(db.String(500))

    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))

    # Session tracking
    session_id = db.Column(db.String(100), index=True)
    referrer = db.Column(db.String(500))

    # Timestamp
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<ResourceView {self.resource_name} at {self.viewed_at}>'


class SearchQuery(db.Model):
    """Track search queries for analytics and improvement."""

    __tablename__ = 'search_queries'

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500), nullable=False, index=True)
    results_count = db.Column(db.Integer)

    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ip_address = db.Column(db.String(45))
    session_id = db.Column(db.String(100), index=True)

    # Search context
    category_filter = db.Column(db.String(100))  # If user filtered by category
    had_results = db.Column(db.Boolean, default=True)

    # Timestamp
    searched_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<SearchQuery "{self.query}" at {self.searched_at}>'


class CategoryView(db.Model):
    """Track category views for popularity analytics."""

    __tablename__ = 'category_views'

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, index=True)

    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ip_address = db.Column(db.String(45))
    session_id = db.Column(db.String(100), index=True)

    # Timestamp
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<CategoryView {self.category_name} at {self.viewed_at}>'


class PageView(db.Model):
    """Track page views for general analytics."""

    __tablename__ = 'page_views'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(500), nullable=False, index=True)
    method = db.Column(db.String(10))  # GET, POST, etc.
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # Response time in seconds

    # User information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    session_id = db.Column(db.String(100), index=True)

    # Referrer and location
    referrer = db.Column(db.String(500))
    country = db.Column(db.String(2))  # ISO country code

    # Timestamp
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<PageView {self.path} at {self.viewed_at}>'


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
