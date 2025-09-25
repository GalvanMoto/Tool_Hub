#!/usr/bin/env python3
"""
Database initialization script for ToolHub.
Creates all database tables and sample data.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, init_database

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        try:
            init_database()
            print("✅ Database initialization completed successfully!")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            sys.exit(1)