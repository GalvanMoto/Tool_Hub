"""
Models module for ToolHub application.
"""

# Import everything from database.py (new models)
from .database import db, bcrypt, User, Usage, AIToolConfig, UserRole, PlanType, init_app

# Define legacy models that some routes might still use
from flask_login import UserMixin
from datetime import datetime
import enum


class SubscriptionType(enum.Enum):
    """Subscription plan types."""
    FREE = "free"
    PRO = "pro"
    LIFETIME = "lifetime"


# User model is imported from database.py - no duplicate definition needed


class Subscription(db.Model):
    """User subscription model."""
    
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.Enum(SubscriptionType), default=SubscriptionType.FREE, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # Null for lifetime plans
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @property
    def is_expired(self):
        """Check if subscription is expired."""
        if self.plan_type == SubscriptionType.LIFETIME:
            return False
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<Subscription {self.plan_type.value} for user {self.user_id}>'


class Tool(db.Model):
    """Tool model for tracking available tools."""
    
    __tablename__ = 'tools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(10), nullable=True)  # Emoji or icon class
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    requires_subscription = db.Column(db.Boolean, default=False, nullable=False)
    usage_limit_free = db.Column(db.Integer, default=10, nullable=True)  # Daily limit for free users
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    usage_records = db.relationship('ToolUsage', backref='tool', lazy=True)
    
    def __repr__(self):
        return f'<Tool {self.name}>'


class ToolUsage(db.Model):
    """Track tool usage for analytics and limits."""
    
    __tablename__ = 'tool_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for anonymous users
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)  # For anonymous tracking
    user_agent = db.Column(db.String(255), nullable=True)
    processing_time = db.Column(db.Float, nullable=True)  # Seconds
    file_size = db.Column(db.Integer, nullable=True)  # Bytes
    success = db.Column(db.Boolean, default=True, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<ToolUsage {self.tool.name} by user {self.user_id}>'


class BlogPost(db.Model):
    """Blog post model."""
    
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    featured_image = db.Column(db.String(255), nullable=True)
    meta_description = db.Column(db.String(160), nullable=True)
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated
    view_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    author = db.relationship('User', backref='blog_posts')
    
    @property
    def tag_list(self):
        """Get tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'


# Import QR models if they exist
try:
    from models.qr import QRCode, QRScan, QRTemplate
except ImportError:
    QRCode = QRScan = QRTemplate = None

__all__ = [
    'db', 'bcrypt', 'User', 'Usage', 'AIToolConfig', 
    'UserRole', 'PlanType', 'init_app', 'Tool', 'ToolUsage', 'Subscription', 'SubscriptionType'
]
