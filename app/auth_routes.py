"""
Authentication routes for user login, signup, and logout.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app.models import db, User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register_auth_routes(bp):
    """Register authentication routes to the blueprint."""

    @bp.route('/signup', methods=['GET', 'POST'])
    def signup():
        """User signup page."""
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            display_name = request.form.get('display_name', '').strip()

            # Validation
            errors = []

            if not username or len(username) < 3:
                errors.append('Username must be at least 3 characters long.')

            if not email or '@' not in email:
                errors.append('Please enter a valid email address.')

            if not password or len(password) < 6:
                errors.append('Password must be at least 6 characters long.')

            if password != confirm_password:
                errors.append('Passwords do not match.')

            # Check if username or email already exists
            if User.query.filter_by(username=username).first():
                errors.append('Username already taken.')

            if User.query.filter_by(email=email).first():
                errors.append('Email already registered.')

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('auth/signup.html')

            # Create new user
            user = User(
                username=username,
                email=email,
                display_name=display_name or username
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            logger.info(f'New user registered: {username}')
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('main.login'))

        return render_template('auth/signup.html')

    @bp.route('/login', methods=['GET', 'POST'])
    def login():
        """User login page."""
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))

        if request.method == 'POST':
            username_or_email = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember', False)

            # Find user by username or email
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()

            if user and user.check_password(password):
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()

                login_user(user, remember=remember)
                logger.info(f'User logged in: {user.username}')

                # Redirect to next page or homepage
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('main.index')

                flash(f'Welcome back, {user.display_name or user.username}!', 'success')
                return redirect(next_page)
            else:
                flash('Invalid username/email or password.', 'error')

        return render_template('auth/login.html')

    @bp.route('/logout')
    @login_required
    def logout():
        """Logout the current user."""
        username = current_user.username
        logout_user()
        logger.info(f'User logged out: {username}')
        flash('You have been logged out.', 'info')
        return redirect(url_for('main.index'))
