"""
Database Query Functions for CodeAI Pakistan
Provides all user and submission management functions
Place at: backend/database/queries.py
"""

from datetime import datetime, UTC
from typing import Optional, Dict, List, Any
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from .db_connector import get_db


# ============================================================================
# USER MANAGEMENT FUNCTIONS
# ============================================================================

def create_user(username: str, password: str, role: str = 'user', email: str = None) -> str:
    """
    Create a new user with hashed password.
    
    Args:
        username: Unique username for the user
        password: Plain text password (will be hashed)
        role: User role - 'user' or 'admin' (default: 'user')
        email: Optional email address
        
    Returns:
        str: User ID if successful, None if failed
        
    Example:
        user_id = create_user('john_doe', 'secure_pass123', 'user', 'john@example.com')
    """
    try:
        db = get_db()
        
        # Check if username already exists
        if db.users.find_one({'username': username}):
            print(f"User '{username}' already exists")
            return None
        
        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Create user document
        user_doc = {
            'username': username,
            'password': hashed_password,
            'role': role,
            'email': email,
            'created_at': datetime.now(UTC),
            'last_login': None,
            'last_visit': None,
            'total_submissions': 0
        }
        
        # Insert user
        result = db.users.insert_one(user_doc)
        
        print(f"✓ User '{username}' created successfully with role '{role}'")
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate user by username and password.
    Updates last_login timestamp on successful authentication.
    
    Args:
        username: Username to authenticate
        password: Plain text password to verify
        
    Returns:
        dict: User document (without password) if authenticated, None otherwise
        
    Example:
        user = authenticate_user('john_doe', 'secure_pass123')
        if user:
            print(f"Welcome {user['username']}!")
    """
    try:
        db = get_db()
        
        # Find user by username
        user = db.users.find_one({'username': username})
        
        if not user:
            print(f"User '{username}' not found")
            return None
        
        # Verify password
        if check_password_hash(user['password'], password):
            # Update last login
            update_last_login(str(user['_id']))
            
            # Remove password from returned user object
            user.pop('password', None)
            
            print(f"✓ User '{username}' authenticated successfully")
            return user
        else:
            print(f"✗ Invalid password for user '{username}'")
            return None
            
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        return None


def get_user_by_username(username: str) -> Optional[Dict]:
    """
    Get user document by username.
    
    Args:
        username: Username to search for
        
    Returns:
        dict: User document (without password) if found, None otherwise
    """
    try:
        db = get_db()
        user = db.users.find_one({'username': username})
        
        if user:
            user.pop('password', None)  # Remove password field
            return user
        return None
        
    except Exception as e:
        print(f"✗ Error fetching user: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Get user document by user ID.
    
    Args:
        user_id: User ObjectId as string
        
    Returns:
        dict: User document (without password) if found, None otherwise
    """
    try:
        db = get_db()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if user:
            user.pop('password', None)
            return user
        return None
        
    except Exception as e:
        print(f"✗ Error fetching user by ID: {e}")
        return None


def update_last_login(user_id: str) -> bool:
    """
    Update user's last login timestamp.
    Called automatically during authentication.
    
    Args:
        user_id: User ObjectId as string
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    try:
        db = get_db()
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.now(UTC)}}
        )
        return result.modified_count > 0
        
    except Exception as e:
        print(f"✗ Error updating last login: {e}")
        return False


def update_last_visit(user_id: str) -> bool:
    """
    Update user's last visit timestamp.
    Should be called on each user activity/page load.
    
    Args:
        user_id: User ObjectId as string
        
    Returns:
        bool: True if updated successfully, False otherwise
    """
    try:
        db = get_db()
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_visit': datetime.now(UTC)}}
        )
        return result.modified_count > 0
        
    except Exception as e:
        print(f"✗ Error updating last visit: {e}")
        return False


def get_all_users(role_filter: str = None) -> List[Dict]:
    """
    Get all users, optionally filtered by role.
    
    Args:
        role_filter: Optional role filter ('user' or 'admin')
        
    Returns:
        list: List of user documents (without passwords)
    """
    try:
        db = get_db()
        
        query = {}
        if role_filter:
            query['role'] = role_filter
        
        users = list(db.users.find(query, {'password': 0}))
        
        return users
        
    except Exception as e:
        print(f"✗ Error fetching users: {e}")
        return []


# ============================================================================
# SUBMISSION MANAGEMENT FUNCTIONS
# ============================================================================

def create_submission(submission_data: Dict) -> str:
    """
    Create a new code analysis submission.
    
    Args:
        submission_data: Dictionary containing submission details:
            - user_id: User ObjectId as string
            - username: Username
            - filename: Uploaded filename
            - language: Programming language
            - analysis_type: Type of analysis performed
            - timestamp: ISO format timestamp
            - results: Analysis results from Gemini
            
    Returns:
        str: Submission ID if successful, None if failed
        
    Example:
        submission_id = create_submission({
            'user_id': '507f1f77bcf86cd799439011',
            'username': 'john_doe',
            'filename': 'app.py',
            'language': 'Python',
            'analysis_type': 'quality',
            'timestamp': datetime.now(UTC).isoformat(),
            'results': {...}
        })
    """
    try:
        db = get_db()
        
        # Ensure required fields
        required_fields = ['user_id', 'username', 'filename', 'language', 'analysis_type']
        for field in required_fields:
            if field not in submission_data:
                print(f"✗ Missing required field: {field}")
                return None
        
        # Add timestamp if not provided
        if 'timestamp' not in submission_data:
            submission_data['timestamp'] = datetime.now(UTC).isoformat()
        
        # Insert submission
        result = db.submissions.insert_one(submission_data)
        
        # Increment user's submission count
        db.users.update_one(
            {'_id': ObjectId(submission_data['user_id'])},
            {'$inc': {'total_submissions': 1}}
        )
        
        print(f"✓ Submission created: {submission_data['filename']} by {submission_data['username']}")
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"✗ Error creating submission: {e}")
        return None


def get_submissions(user_id: str = None, limit: int = 50, skip: int = 0) -> List[Dict]:
    """
    Get submissions, optionally filtered by user.
    
    Args:
        user_id: Optional user ID to filter submissions
        limit: Maximum number of submissions to return
        skip: Number of submissions to skip (for pagination)
        
    Returns:
        list: List of submission documents
        
    Example:
        # Get all submissions for a user
        submissions = get_submissions(user_id='507f1f77bcf86cd799439011', limit=20)
    """
    try:
        db = get_db()
        
        query = {}
        if user_id:
            query['user_id'] = user_id
        
        submissions = list(
            db.submissions
            .find(query)
            .sort('timestamp', -1)
            .skip(skip)
            .limit(limit)
        )
        
        return submissions
        
    except Exception as e:
        print(f"✗ Error fetching submissions: {e}")
        return []


def get_submission_by_id(submission_id: str) -> Optional[Dict]:
    """
    Get a specific submission by ID.
    
    Args:
        submission_id: Submission ObjectId as string
        
    Returns:
        dict: Submission document if found, None otherwise
    """
    try:
        db = get_db()
        submission = db.submissions.find_one({'_id': ObjectId(submission_id)})
        return submission
        
    except Exception as e:
        print(f"✗ Error fetching submission: {e}")
        return None


def get_submission_stats(filters: Dict = None) -> Dict:
    """
    Get aggregated submission statistics.
    
    Args:
        filters: Optional filters dictionary:
            - start_date: ISO format start date
            - end_date: ISO format end date
            - language: Filter by programming language
            - user: Filter by username
            
    Returns:
        dict: Statistics including total submissions, by language, by type, etc.
        
    Example:
        stats = get_submission_stats({
            'start_date': '2024-01-01',
            'language': 'Python'
        })
    """
    try:
        db = get_db()
        
        # Build match query
        match_query = {}
        if filters:
            if filters.get('start_date'):
                match_query['timestamp'] = {'$gte': filters['start_date']}
            if filters.get('end_date'):
                if 'timestamp' in match_query:
                    match_query['timestamp']['$lte'] = filters['end_date']
                else:
                    match_query['timestamp'] = {'$lte': filters['end_date']}
            if filters.get('language'):
                match_query['language'] = filters['language']
            if filters.get('user'):
                match_query['username'] = filters['user']
        
        # Total submissions
        total = db.submissions.count_documents(match_query)
        
        # Submissions by language
        by_language = list(db.submissions.aggregate([
            {'$match': match_query},
            {'$group': {'_id': '$language', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]))
        
        # Submissions by analysis type
        by_type = list(db.submissions.aggregate([
            {'$match': match_query},
            {'$group': {'_id': '$analysis_type', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]))
        
        # Submissions by user
        by_user = list(db.submissions.aggregate([
            {'$match': match_query},
            {'$group': {'_id': '$username', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 10}
        ]))
        
        return {
            'total_submissions': total,
            'by_language': by_language,
            'by_analysis_type': by_type,
            'top_users': by_user
        }
        
    except Exception as e:
        print(f"✗ Error getting submission stats: {e}")
        return {
            'total_submissions': 0,
            'by_language': [],
            'by_analysis_type': [],
            'top_users': []
        }


def get_bug_statistics(filters: Dict = None) -> Dict:
    """
    Get bug detection statistics from submissions.
    
    Args:
        filters: Optional filters (same as get_submission_stats)
        
    Returns:
        dict: Bug statistics including total bugs found, by severity, etc.
    """
    try:
        db = get_db()
        
        # Build match query
        match_query = {'analysis_type': 'bugs_and_tests'}
        if filters:
            if filters.get('start_date'):
                match_query['timestamp'] = {'$gte': filters['start_date']}
            if filters.get('end_date'):
                if 'timestamp' in match_query:
                    match_query['timestamp']['$lte'] = filters['end_date']
                else:
                    match_query['timestamp'] = {'$lte': filters['end_date']}
            if filters.get('language'):
                match_query['language'] = filters['language']
            if filters.get('severity'):
                match_query['results.bugs.severity'] = filters['severity']
        
        # Get all bug submissions
        submissions = list(db.submissions.find(match_query, {'results': 1, 'language': 1}))
        
        total_bugs = 0
        by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        by_language = {}
        
        for sub in submissions:
            results = sub.get('results', {})
            bugs = results.get('bugs', [])
            language = sub.get('language', 'Unknown')
            
            total_bugs += len(bugs)
            
            for bug in bugs:
                severity = bug.get('severity', 'unknown').lower()
                if severity in by_severity:
                    by_severity[severity] += 1
                
            if language not in by_language:
                by_language[language] = 0
            by_language[language] += len(bugs)
        
        return {
            'total_bugs_detected': total_bugs,
            'by_severity': by_severity,
            'by_language': by_language,
            'total_scans': len(submissions)
        }
        
    except Exception as e:
        print(f"✗ Error getting bug statistics: {e}")
        return {
            'total_bugs_detected': 0,
            'by_severity': {},
            'by_language': {},
            'total_scans': 0
        }


def get_recent_submissions(limit: int = 10, filters: Dict = None) -> List[Dict]:
    """
    Get most recent submissions.
    
    Args:
        limit: Maximum number of submissions to return
        filters: Optional filters (same as get_submission_stats)
        
    Returns:
        list: List of recent submission documents
    """
    try:
        db = get_db()
        
        match_query = {}
        if filters:
            if filters.get('start_date'):
                match_query['timestamp'] = {'$gte': filters['start_date']}
            if filters.get('end_date'):
                if 'timestamp' in match_query:
                    match_query['timestamp']['$lte'] = filters['end_date']
                else:
                    match_query['timestamp'] = {'$lte': filters['end_date']}
            if filters.get('language'):
                match_query['language'] = filters['language']
            if filters.get('user'):
                match_query['username'] = filters['user']
        
        submissions = list(
            db.submissions
            .find(match_query, {
                'filename': 1,
                'language': 1,
                'username': 1,
                'analysis_type': 1,
                'timestamp': 1,
                'results.overall_score': 1,
                'results.bugs_found': 1
            })
            .sort('timestamp', -1)
            .limit(limit)
        )
        
        return submissions
        
    except Exception as e:
        print(f"✗ Error fetching recent submissions: {e}")
        return []


def delete_submission(submission_id: str) -> bool:
    """
    Delete a submission by ID.
    
    Args:
        submission_id: Submission ObjectId as string
        
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        db = get_db()
        result = db.submissions.delete_one({'_id': ObjectId(submission_id)})
        return result.deleted_count > 0
        
    except Exception as e:
        print(f"✗ Error deleting submission: {e}")
        return False