"""
MongoDB database connector for CodeAI Pakistan
Handles connection initialization and provides database access
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection settings
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'codeai_pakistan')

# Global database connection
_db = None
_client = None

def init_db():
    """Initialize MongoDB connection"""
    global _db, _client
    
    try:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        _client.admin.command('ping')
        _db = _client[DB_NAME]
        
        # Create indexes for better performance
        _db.users.create_index("username", unique=True)
        _db.submissions.create_index([("user_id", 1), ("timestamp", -1)])
        _db.submissions.create_index("language")
        _db.submissions.create_index("timestamp")
        
        print(f"✅ Connected to MongoDB: {DB_NAME}")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("⚠️  Please ensure MongoDB is running")
        return False
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def get_db():
    """Get database instance"""
    global _db
    if _db is None:
        init_db()
    return _db

def close_db():
    """Close database connection"""
    global _client
    if _client:
        _client.close()
        print("MongoDB connection closed")

# Database collections
def get_users_collection():
    return get_db().users

def get_submissions_collection():
    return get_db().submissions

def get_bugs_collection():
    return get_db().bugs

def get_documentation_collection():
    return get_db().documentation