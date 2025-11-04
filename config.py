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

    # Claude API settings (for future use)
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')

    # Application settings
    APP_NAME = "Teaching Resources Hub"
    APP_VERSION = "1.0.0"
