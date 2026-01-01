"""
Database Initialization Script

Run this script to create all required tables in the database.
Can be run locally or on Railway.

Usage:
    Local:   python init_database.py
    Railway: railway run python init_database.py
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Display connection info (without password)
database_url = os.getenv("DATABASE_URL", "")
if database_url:
    # Mask the password for display
    parts = database_url.split("@")
    if len(parts) > 1:
        print(f"🔗 Connecting to: ...@{parts[1]}")
else:
    print(f"🔗 Connecting to: {os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'chatbot_psb')}")

print("=" * 50)
print("📦 Initializing Database Tables...")
print("=" * 50)

try:
    from database import init_db, check_database_connection, Base, engine
    
    # Test connection first
    print("\n🔍 Testing database connection...")
    if check_database_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        exit(1)
    
    # Create tables
    print("\n📝 Creating tables...")
    init_db()
    
    # List created tables
    print("\n📋 Tables in database:")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n  📁 {table}")
        for col in columns:
            print(f"      - {col['name']}: {col['type']}")
    
    print("\n" + "=" * 50)
    print("✅ Database initialization complete!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
