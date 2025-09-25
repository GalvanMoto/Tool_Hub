"""
Database models for ToolHub application.
Handles user authentication, usage tracking, and freemium limitations.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, date
from enum import Enum

db = SQLAlchemy()
bcrypt = Bcrypt()


class UserRole(Enum):
    """User role enumeration for freemium system."""
    FREE = "free"
    PREMIUM = "premium"


class PlanType(Enum):
    """Premium plan types."""
    MONTHLY = "monthly"
    YEARLY = "yearly" 
    LIFETIME = "lifetime"


class User(UserMixin, db.Model):
    """User model with freemium support."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.FREE, nullable=False)
    plan_type = db.Column(db.Enum(PlanType), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship to usage records
    usage_records = db.relationship('Usage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the hash."""
        try:
            # Try bcrypt first (new format)
            return bcrypt.check_password_hash(self.password_hash, password)
        except ValueError as bcrypt_error:
            # Fall back to Werkzeug's check for old scrypt format
            try:
                from werkzeug.security import check_password_hash
                print(f"Trying legacy password check for user {self.username}")
                is_valid = check_password_hash(self.password_hash, password)
                
                # If valid with old format, update to new bcrypt format
                if is_valid:
                    print(f"Converting password format for user {self.username}")
                    self.set_password(password)
                    db.session.commit()
                    print(f"Successfully updated password format for user {self.username}")
                
                return is_valid
            except Exception as werkzeug_error:
                print(f"Password verification failed for user {self.username}")
                print(f"Bcrypt error: {bcrypt_error}")
                print(f"Werkzeug error: {werkzeug_error}")
                print(f"Hash format: {self.password_hash[:20] if self.password_hash else 'None'}...")
                return False
    
    def is_premium(self):
        """Check if user has premium access."""
        return self.role == UserRole.PREMIUM
    
    def get_daily_usage_count(self, tool_name=None, target_date=None):
        """Get usage count for today or specific date."""
        if target_date is None:
            target_date = date.today()
        
        query = self.usage_records.filter(
            db.func.date(Usage.used_at) == target_date
        )
        
        if tool_name:
            query = query.filter(Usage.tool_name == tool_name)
        
        return query.count()
    
    def can_use_tool(self, tool_name):
        """Check if user can use a tool (freemium logic)."""
        if self.is_premium():
            return True
        
        # Free users: 3 uses per day across all AI tools
        daily_usage = self.get_daily_usage_count()
        return daily_usage < 3
    
    def record_usage(self, tool_name):
        """Record tool usage for freemium tracking."""
        usage = Usage(
            user_id=self.id,
            tool_name=tool_name,
            used_at=datetime.utcnow()
        )
        db.session.add(usage)
        db.session.commit()


class Usage(db.Model):
    """Usage tracking model for freemium limits."""
    __tablename__ = 'usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tool_name = db.Column(db.String(100), nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Optional: store input/output for analytics
    input_data = db.Column(db.Text, nullable=True)
    output_data = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Usage {self.user_id}:{self.tool_name}:{self.used_at}>'


class AIToolConfig(db.Model):
    """Configuration for AI tools (API keys, limits, etc.)."""
    __tablename__ = 'ai_tool_config'
    
    id = db.Column(db.Integer, primary_key=True)
    tool_name = db.Column(db.String(100), unique=True, nullable=False)
    is_enabled = db.Column(db.Boolean, default=True, nullable=False)
    daily_limit_free = db.Column(db.Integer, default=3, nullable=False)
    daily_limit_premium = db.Column(db.Integer, default=-1, nullable=False)  # -1 = unlimited
    config_json = db.Column(db.JSON, nullable=True)  # For storing tool-specific config
    
    def __repr__(self):
        return f'<AIToolConfig {self.tool_name}>'


def init_app(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    bcrypt.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default AI tool configurations
        create_default_ai_tools()


def create_default_ai_tools():
    """Create default AI tool configurations."""
    ai_tools = [
        'blog_generator',
        'article_summarizer', 
        'paraphraser',
        'grammar_checker',
        'headline_generator',
        'meta_description_generator',
        'product_description_generator',
        'email_writer',
        'social_media_generator',
        'ad_copy_generator',
        'content_rewriter',
        'content_expander',
        'outline_generator',
        'faq_generator',
        'interview_questions',
        'resume_bullets'
    ]
    
    for tool_name in ai_tools:
        existing = AIToolConfig.query.filter_by(tool_name=tool_name).first()
        if not existing:
            config = AIToolConfig(
                tool_name=tool_name,
                is_enabled=True,
                daily_limit_free=3,
                daily_limit_premium=-1
            )
            db.session.add(config)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default AI tools: {e}")