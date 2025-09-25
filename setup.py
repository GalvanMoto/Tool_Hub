#!/usr/bin/env python3
"""
ToolHub Setup Script
====================
Development environment setup and database initialization script.

This script helps:
- Initialize the database with proper schema
- Create sample data for testing
- Set up admin users
- Configure environment variables
"""

import os
import sys
import getpass
from datetime import datetime
from app import create_app
from models.database import db, User, Usage, AIToolConfig, UserRole, PlanType


def setup_database(app):
    """Initialize database tables using Flask-Migrate."""
    with app.app_context():
        print("🔧 Setting up database...")
        
        # Check if migration directory exists
        if not os.path.exists('migrations'):
            print("❌ Migration directory not found!")
            print("Please run: flask db init")
            return False
            
        # Run migrations
        try:
            from flask_migrate import upgrade
            upgrade()
            print("✅ Database migrations applied successfully!")
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
            
        return True


def create_admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        print("\n👤 Creating Admin User")
        print("======================")
        
        # Get admin details
        admin_email = input("Enter admin email (admin@toolhub.com): ").strip()
        if not admin_email:
            admin_email = "admin@toolhub.com"
        
        admin_username = input("Enter admin username (admin): ").strip()
        if not admin_username:
            admin_username = "admin"
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"⚠️  Admin user already exists with email: {admin_email}")
            return existing_admin
        
        # Get password securely
        while True:
            admin_password = getpass.getpass("Enter admin password: ").strip()
            if len(admin_password) >= 6:
                break
            print("Password must be at least 6 characters long!")
        
        # Create admin user
        try:
            admin = User(
                email=admin_email,
                username=admin_username,
                role=UserRole.PREMIUM,  # Give admin premium access
                plan_type=PlanType.LIFETIME
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Admin user created successfully!")
            print(f"   Email: {admin_email}")
            print(f"   Username: {admin_username}")
            print(f"   Role: {admin.role.value}")
            print(f"   Plan: {admin.plan_type.value if admin.plan_type else 'None'}")
            
            return admin
            
        except Exception as e:
            print(f"❌ Failed to create admin user: {e}")
            db.session.rollback()
            return None


def setup_ai_tool_configs(app):
    """Set up AI tool configurations."""
    with app.app_context():
        print("\n🤖 Setting up AI Tool Configurations")
        print("====================================")
        
        ai_tools = [
            {
                'tool_name': 'blog_generator',
                'is_enabled': True,
                'daily_limit_free': 3,
                'daily_limit_premium': 50,
                'config_json': {'display_name': 'Blog Generator', 'description': 'Generate high-quality blog content'}
            },
            {
                'tool_name': 'email_writer',
                'is_enabled': True,
                'daily_limit_free': 5,
                'daily_limit_premium': 100,
                'config_json': {'display_name': 'Email Writer', 'description': 'Create professional emails for various purposes'}
            },
            {
                'tool_name': 'social_media_generator',
                'is_enabled': True,
                'daily_limit_free': 5,
                'daily_limit_premium': 75,
                'config_json': {'display_name': 'Social Media Generator', 'description': 'Generate engaging social media posts'}
            },
            {
                'tool_name': 'ad_copy_generator',
                'is_enabled': True,
                'daily_limit_free': 2,
                'daily_limit_premium': 30,
                'config_json': {'display_name': 'Ad Copy Generator', 'description': 'Create compelling advertisement copy'}
            },
            {
                'tool_name': 'headline_generator',
                'is_enabled': True,
                'daily_limit_free': 10,
                'daily_limit_premium': 200,
                'config_json': {'display_name': 'Headline Generator', 'description': 'Generate catchy and SEO-friendly headlines'}
            },
            {
                'tool_name': 'product_description_generator',
                'is_enabled': True,
                'daily_limit_free': 3,
                'daily_limit_premium': 50,
                'config_json': {'display_name': 'Product Description Generator', 'description': 'Create compelling product descriptions'}
            },
            {
                'tool_name': 'meta_description_generator',
                'is_enabled': True,
                'daily_limit_free': 10,
                'daily_limit_premium': 150,
                'config_json': {'display_name': 'Meta Description Generator', 'description': 'Generate SEO-optimized meta descriptions'}
            },
            {
                'tool_name': 'paraphraser',
                'is_enabled': True,
                'daily_limit_free': 8,
                'daily_limit_premium': 120,
                'config_json': {'display_name': 'Paraphraser', 'description': 'Rewrite text while maintaining meaning'}
            },
            {
                'tool_name': 'article_summarizer',
                'is_enabled': True,
                'daily_limit_free': 5,
                'daily_limit_premium': 80,
                'config_json': {'display_name': 'Article Summarizer', 'description': 'Summarize long articles and content'}
            },
            {
                'tool_name': 'content_rewriter',
                'is_enabled': True,
                'daily_limit_free': 4,
                'daily_limit_premium': 60,
                'config_json': {'display_name': 'Content Rewriter', 'description': 'Rewrite content for freshness and uniqueness'}
            }
        ]
        
        created_count = 0
        for config_data in ai_tools:
            existing_config = AIToolConfig.query.filter_by(tool_name=config_data['tool_name']).first()
            if not existing_config:
                config = AIToolConfig(**config_data)
                db.session.add(config)
                created_count += 1
                print(f"   ✅ {config_data['config_json']['display_name']}")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✅ Created {created_count} AI tool configurations!")
        else:
            print("ℹ️  All AI tool configurations already exist.")


def create_env_file():
    """Create .env file from template."""
    print("\n🔐 Environment Configuration")
    print("============================")
    
    if os.path.exists('.env'):
        print("ℹ️  .env file already exists.")
        return
    
    env_template = """# ToolHub Environment Configuration
# Database
DATABASE_URL=sqlite:///toolhub_dev.db

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# Google Gemini API (for AI tools)
GEMINI_API_KEY=your-gemini-api-key-here

# Application Settings
MAX_CONTENT_LENGTH=16777216  # 16MB max file upload
"""
    
    create_env = input("Create .env file with default configuration? (Y/n): ").strip().lower()
    if create_env in ['', 'y', 'yes']:
        with open('.env', 'w') as f:
            f.write(env_template)
        print("✅ .env file created!")
        print("⚠️  Please edit .env file and add your API keys.")
    else:
        print("⏭️  Skipping .env file creation.")


def display_summary():
    """Display setup summary and next steps."""
    print("\n🎉 ToolHub Setup Complete!")
    print("==========================")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Add your Gemini API key for AI tools")
    print("3. Start the development server:")
    print("   python -c \"from app import create_app; app = create_app(); app.run(debug=True, port=5001)\"")
    print("\nAvailable features:")
    print("• 8 SEO Analysis Tools (API-free)")
    print("• 10+ AI Content Creation Tools")
    print("• User Authentication & Management")
    print("• Freemium Usage Tracking")
    print("• Responsive Web Interface")
    print("\nAccess the app at: http://127.0.0.1:5001")


def main():
    """Main setup function."""
    print("🚀 ToolHub Development Setup")
    print("============================")
    print("Welcome to ToolHub - Your AI-Powered Productivity Suite")
    print()
    
    # Create Flask app
    try:
        app = create_app()
        print("✅ Flask app created successfully!")
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        sys.exit(1)
    
    # Setup environment file
    create_env_file()
    
    # Setup database
    if not setup_database(app):
        print("❌ Database setup failed!")
        sys.exit(1)
    
    # Setup AI tool configurations
    setup_ai_tool_configs(app)
    
    # Ask if user wants to create admin account
    create_admin = input("\nCreate admin user? (Y/n): ").strip().lower()
    if create_admin in ['', 'y', 'yes']:
        create_admin_user(app)
    
    # Display summary
    display_summary()


if __name__ == '__main__':
    main()