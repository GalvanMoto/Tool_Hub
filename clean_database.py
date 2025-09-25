#!/usr/bin/env python3
"""
Database Cleaning Script for ToolHub
====================================
This script completely cleans the database by dropping all tables and recreating them.
Use with caution - this will delete ALL data!
"""

import os
import sys
from app import create_app
from models.database import db


def clean_database():
    """Drop all tables and recreate them."""
    print("🗑️  ToolHub Database Cleaning Script")
    print("===================================")
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    
    # Confirm action
    confirm = input("Are you sure you want to continue? Type 'YES' to confirm: ").strip()
    if confirm != 'YES':
        print("❌ Operation cancelled.")
        return False
    
    try:
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            print("\n🔄 Dropping all database tables...")
            
            # Drop all tables
            db.drop_all()
            print("✅ All tables dropped successfully!")
            
            print("🔄 Creating fresh database schema...")
            
            # Create all tables
            db.create_all()
            print("✅ Fresh database schema created!")
            
            print("\n🎉 Database cleaned successfully!")
            print("💡 You can now run setup.py to initialize with fresh data.")
            
            return True
            
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        return False


if __name__ == '__main__':
    success = clean_database()
    if success:
        print("\nNext steps:")
        print("1. Run: python setup.py")
        print("2. Create admin user and configure AI tools")
        print("3. Start the application: python app.py")
    else:
        print("Database cleaning failed!")
        sys.exit(1)