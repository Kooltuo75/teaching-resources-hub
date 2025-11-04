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

    # Google Classroom Integration
    google_id = db.Column(db.String(100), unique=True, nullable=True)  # Google account ID
    google_access_token = db.Column(db.Text, nullable=True)  # Encrypted access token
    google_refresh_token = db.Column(db.Text, nullable=True)  # Encrypted refresh token
    google_token_expiry = db.Column(db.DateTime, nullable=True)  # Token expiration time
    google_connected = db.Column(db.Boolean, default=False)  # Is Google Classroom connected?

    # Relationships
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def get_profile_url(self):
        """Get the URL to this user's profile."""
        return f'/profile/{self.username}'

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


def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
