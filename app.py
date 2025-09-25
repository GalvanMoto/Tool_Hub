# Main application entry point

"""
ToolHub Flask Application
A SaaS platform for productivity tools.
"""

import os
from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
from models.database import db, User, init_app as init_models

# Load environment variables
load_dotenv()

# Import blueprints
from routes.main import main
from routes.tools import tools
from routes.auth import auth
from routes.ai_tools import ai_tools


def create_app(config_name='development'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    init_models(app)
    migrate = Migrate(app, db)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Check Gemini API configuration
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key:
        app.logger.info("Gemini API key found - AI tools will be available")
    else:
        app.logger.warning("Gemini API key not found in environment variables")
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(tools)
    app.register_blueprint(auth)
    app.register_blueprint(ai_tools)
    
    # Note: Database tables will be created when needed
    
    return app


def init_database():
    """Initialize database tables and sample data."""
    from models.database import db
    from models import Tool
    
    db.create_all()
    
    tools_data = [
            {
                'name': 'PDF Merge',
                'slug': 'pdf-merge',
                'description': 'Combine multiple PDF files into one document',
                'icon': '📄',
                'category': 'Document'
            },
            {
                'name': 'Image Resizer',
                'slug': 'image-resizer',
                'description': 'Resize images while maintaining quality',
                'icon': '🖼️',
                'category': 'Image'
            },
            {
                'name': 'QR Code Generator',
                'slug': 'qr-generator',
                'description': 'Generate QR codes for text, URLs, and more',
                'icon': '📱',
                'category': 'Utility'
            },
            # SEO Tools
            {
                'name': 'SEO & Marketing Toolkit',
                'slug': 'seo-tools',
                'description': 'Complete SEO toolkit with audit, keyword research, and analytics',
                'icon': '🔍',
                'category': 'SEO'
            },
            {
                'name': 'SEO Audit',
                'slug': 'seo-audit',
                'description': 'Comprehensive analysis of your website\'s SEO health',
                'icon': '🔍',
                'category': 'SEO'
            },
            {
                'name': 'Keyword Research',
                'slug': 'keyword-research',
                'description': 'Discover high-value keywords with search volume and difficulty',
                'icon': '🔑',
                'category': 'SEO'
            },
            {
                'name': 'Backlink Checker',
                'slug': 'backlink-checker',
                'description': 'Analyze backlink profile and link building opportunities',
                'icon': '🔗',
                'category': 'SEO'
            },
            {
                'name': 'Domain Overview',
                'slug': 'domain-overview',
                'description': 'Get comprehensive domain metrics and authority scores',
                'icon': '🌐',
                'category': 'SEO'
            },
            {
                'name': 'Traffic Analytics',
                'slug': 'traffic-analytics',
                'description': 'Monitor website traffic sources and engagement metrics',
                'icon': '📊',
                'category': 'SEO'
            },
            {
                'name': 'On-Page SEO Checker',
                'slug': 'onpage-seo',
                'description': 'Optimize individual pages for better search rankings',
                'icon': '📝',
                'category': 'SEO'
            },
            {
                'name': 'Competitor Analysis',
                'slug': 'competitor-analysis',
                'description': 'Compare your website performance against competitors',
                'icon': '⚔️',
                'category': 'SEO'
            },
            {
                'name': 'Content Analyzer',
                'slug': 'content-analyzer',
                'description': 'Analyze content readability and SEO optimization',
                'icon': '📄',
                'category': 'SEO'
            },
            {
                'name': 'SERP Tracking',
                'slug': 'serp-tracking',
                'description': 'Track keyword rankings across search engines',
                'icon': '📈',
                'category': 'SEO'
            },
            {
                'name': 'Site Speed Test',
                'slug': 'site-speed',
                'description': 'Test website loading speed and get optimization tips',
                'icon': '⚡',
                'category': 'SEO'
            },
            {
                'name': 'Ad Campaign Research',
                'slug': 'ad-research',
                'description': 'Research competitor ad strategies and profitable keywords',
                'icon': '💰',
                'category': 'SEO'
            }
        ]
    
    for tool_data in tools_data:
        existing_tool = Tool.query.filter_by(slug=tool_data['slug']).first()
        if not existing_tool:
            tool = Tool(**tool_data)
            db.session.add(tool)
    
    db.session.commit()
    print("Database initialized successfully!")


def register_auth_blueprint(app):
    """Register authentication blueprint (to be implemented)."""
    # TODO: Create auth blueprint with login/signup routes
    pass


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)

