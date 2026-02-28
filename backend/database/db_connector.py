"""
MongoDB Connection Manager for CodeAI Pakistan
Handles database initialization and connection management
Place at: backend/database/db_connector.py
"""

import os
from pymongo import MongoClient, errors
from pymongo.database import Database
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apikey.env'))

# Global database connection
_db_client = None
_db = None


def init_db() -> bool:
    """
    Initialize MongoDB connection and set up collections with indexes.
    
    Returns:
        bool: True if initialization successful, False otherwise
        
    Raises:
        Exception: If connection fails or environment variables missing
    """
    global _db_client, _db
    
    try:
        # Get MongoDB configuration from environment
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.environ.get('MONGODB_DB_NAME', 'codeai_pakistan')
        
        if not mongodb_uri or not db_name:
            raise ValueError("MongoDB configuration missing in environment variables")
        
        print(f"Connecting to MongoDB: {mongodb_uri}")
        
        # Create MongoDB client with timeout
        _db_client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000
        )
        
        # Test connection
        _db_client.admin.command('ping')
        
        # Get database
        _db = _db_client[db_name]
        
        # Create collections if they don't exist and set up indexes
        _setup_collections()
        
        print(f"✓ MongoDB connected successfully to database: {db_name}")
        return True
        
    except errors.ConnectionFailure as e:
        print(f"✗ MongoDB connection failed: {e}")
        _db_client = None
        _db = None
        return False
        
    except errors.ServerSelectionTimeoutError as e:
        print(f"✗ MongoDB server selection timeout: {e}")
        print("  Make sure MongoDB is running on the specified URI")
        _db_client = None
        _db = None
        return False
        
    except Exception as e:
        print(f"✗ MongoDB initialization error: {e}")
        _db_client = None
        _db = None
        return False


def _setup_collections():
    """
    Set up database collections with appropriate indexes for performance.
    Creates collections if they don't exist and adds indexes.
    """
    try:
        # Users collection
        if 'users' not in _db.list_collection_names():
            _db.create_collection('users')
            print("  Created 'users' collection")
        
        # Create indexes for users
        _db.users.create_index('username', unique=True)
        _db.users.create_index('email', sparse=True)
        _db.users.create_index('role')
        _db.users.create_index('last_login')
        
        # Submissions collection
        if 'submissions' not in _db.list_collection_names():
            _db.create_collection('submissions')
            print("  Created 'submissions' collection")
        
        # Create indexes for submissions
        _db.submissions.create_index('user_id')
        _db.submissions.create_index('username')
        _db.submissions.create_index('timestamp')
        _db.submissions.create_index('language')
        _db.submissions.create_index('analysis_type')
        _db.submissions.create_index([('user_id', 1), ('timestamp', -1)])
        
        print("  Database indexes created successfully")
        
    except Exception as e:
        print(f"  Warning: Error setting up collections: {e}")


def get_db() -> Database:
    """
    Get the MongoDB database instance.
    Initializes connection if not already established.
    
    Returns:
        Database: MongoDB database object
        
    Raises:
        Exception: If database connection not initialized
    """
    global _db
    
    if _db is None:
        init_db()
    
    if _db is None:
        raise Exception("Database connection not initialized. Call init_db() first.")
    
    return _db


def close_db():
    """
    Close MongoDB connection.
    Should be called when application shuts down.
    """
    global _db_client, _db
    
    if _db_client:
        _db_client.close()
        _db_client = None
        _db = None
        print("✓ MongoDB connection closed")


def is_connected() -> bool:
    """
    Check if database connection is active.
    
    Returns:
        bool: True if connected, False otherwise
    """
    global _db_client
    
    if _db_client is None:
        return False
    
    try:
        _db_client.admin.command('ping')
        return True
    except Exception:
        return False


def get_collection_stats() -> dict:
    """
    Get statistics about database collections.
    
    Returns:
        dict: Collection statistics including document counts
    """
    if _db is None:
        return {"error": "Database not initialized"}
    
    try:
        return {
            "users_count": _db.users.count_documents({}),
            "submissions_count": _db.submissions.count_documents({}),
            "collections": _db.list_collection_names()
        }
    except Exception as e:
        return {"error": str(e)}