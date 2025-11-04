"""
Configuration settings for the Teaching Resources application.
"""
import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).parent

class Config:
    """Base configuration class."""

    # Base directory
    BASE_DIR = BASE_DIR

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True

    # Database settings
    DATABASE_PATH = BASE_DIR / 'data' / 'teaching_resources.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR / "data" / "users.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Claude API settings (for future use)
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')

    # Google OAuth Settings
    # Get these from https://console.cloud.google.com/
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_CLIENT_ID_HERE')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_CLIENT_SECRET_HERE')
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

    # Google Classroom API Scopes
    GOOGLE_SCOPES = [
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.coursework.students',
        'https://www.googleapis.com/auth/classroom.announcements'
    ]

    # Application settings
    APP_NAME = "Teaching Resources Hub"
    APP_VERSION = "1.0.0"
