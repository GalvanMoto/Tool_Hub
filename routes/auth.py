"""
Authentication routes for ToolHub application.
Handles user registration, login, logout, and account management with freemium support.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models import db, User, UserRole, PlanType
import re

auth = Blueprint('auth', __name__)


def is_valid_email(email):
    """Simple email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@auth.route('/register', methods=['GET', 'POST'])
@auth.route('/signup', methods=['GET', 'POST']) 
def register():
    """User registration with freemium support."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not email or not is_valid_email(email):
            errors.append('Please enter a valid email address.')
        
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
            
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')
        
        if User.query.filter_by(username=username).first():
            errors.append('Username is already taken.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user with FREE role by default
        user = User(
            username=username,
            email=email,
            role=UserRole.FREE
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Auto-login the new user
            login_user(user)
            flash('Welcome to ToolHub! You have 3 free AI tool uses per day.', 'success')
            
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        login_identifier = request.form.get('login_identifier', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        if not login_identifier or not password:
            flash('Please enter both email/username and password.', 'error')
            return render_template('auth/login.html')
        
        # Find user by email or username
        user = User.query.filter(
            (User.email == login_identifier.lower()) |
            (User.username == login_identifier)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return render_template('auth/login.html')
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember_me)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            role_message = "Premium" if user.is_premium() else "Free (3 AI tools/day)"
            flash(f'Welcome back, {user.username}! ({role_message})', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email/username or password.', 'error')
    
    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    """User logout."""
    username = current_user.username
    logout_user()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/profile')
@login_required
def profile():
    """User profile page."""
    daily_usage = current_user.get_daily_usage_count()
    usage_limit = 3 if not current_user.is_premium() else "Unlimited"
    
    return render_template('auth/profile.html', 
                         user=current_user, 
                         daily_usage=daily_usage,
                         usage_limit=usage_limit)


@auth.route('/upgrade')
@login_required
def upgrade():
    """Upgrade to premium page."""
    if current_user.is_premium():
        flash('You already have a premium account!', 'info')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/upgrade.html')