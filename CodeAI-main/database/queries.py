"""
Database query functions for CodeAI Pakistan
Handles all CRUD operations for users, submissions, bugs, and documentation
"""

from datetime import datetime, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_connector import (
    get_users_collection, 
    get_submissions_collection
)

# --------------------
# User Management
# --------------------
def create_user(username, password, role="user"):
    """Create a new user with hashed password"""
    try:
        users = get_users_collection()
        
        # Check if user already exists
        if users.find_one({"username": username}):
            return None
        
        user_doc = {
            "username": username,
            "password": generate_password_hash(password),
            "role": role,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        result = users.insert_one(user_doc)
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def authenticate_user(username, password):
    """Authenticate user and return user document if valid"""
    try:
        users = get_users_collection()
        user = users.find_one({"username": username})
        
        if user and check_password_hash(user['password'], password):
            # Update last login
            users.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return user
        
        return None
        
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

def get_user_by_username(username):
    """Get user by username"""
    try:
        users = get_users_collection()
        return users.find_one({"username": username})
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        users = get_users_collection()
        return users.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None

# --------------------
# Submission Management
# --------------------
def create_submission(submission_data):
    """
    Create a new code submission record
    
    submission_data should include:
    - user_id: str
    - username: str
    - filename: str
    - language: str
    - code_snippet: str (truncated code for display)
    - timestamp: str (ISO format)
    - scores: dict (all quality metrics)
    - bugs: list of bug dicts
    - documentation: dict with english/urdu keys
    - corrected_code: str (optional)
    """
    try:
        submissions = get_submissions_collection()
        result = submissions.insert_one(submission_data)
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"Error creating submission: {e}")
        return None

def get_submissions(user_id=None, limit=50, skip=0, filters=None):
    """Get submissions with optional filtering"""
    try:
        submissions = get_submissions_collection()
        
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        if filters:
            if filters.get('language'):
                query["language"] = filters['language']
            
            if filters.get('start_date') and filters.get('end_date'):
                query["timestamp"] = {
                    "$gte": filters['start_date'],
                    "$lte": filters['end_date']
                }
        
        cursor = submissions.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        return list(cursor)
        
    except Exception as e:
        print(f"Error getting submissions: {e}")
        return []

def get_submission_by_id(submission_id):
    """Get single submission by ID"""
    try:
        submissions = get_submissions_collection()
        return submissions.find_one({"_id": ObjectId(submission_id)})
    except Exception as e:
        print(f"Error getting submission: {e}")
        return None

# --------------------
# Statistics and Analytics
# --------------------
def get_submission_stats(filters=None):
    """
    Get aggregate statistics for submissions
    Returns:
    - total_submissions: int
    - avg_overall_score: float
    - avg_score_by_language: dict
    - submissions_by_language: dict
    - quality_distribution: dict (High/Medium/Low counts)
    """
    try:
        submissions = get_submissions_collection()
        
        # Build match query from filters
        match_query = {}
        if filters:
            if filters.get('language'):
                match_query["language"] = filters['language']
            if filters.get('user'):
                match_query["username"] = filters['user']
            if filters.get('start_date') and filters.get('end_date'):
                match_query["timestamp"] = {
                    "$gte": filters['start_date'],
                    "$lte": filters['end_date']
                }
        
        # Total submissions
        total = submissions.count_documents(match_query)
        
        # Average overall score
        pipeline = [
            {"$match": match_query},
            {"$group": {
                "_id": None,
                "avg_overall": {"$avg": "$scores.overall"},
                "avg_complexity": {"$avg": "$scores.complexity"},
                "avg_coverage": {"$avg": "$scores.estimated_coverage"}
            }}
        ]
        
        avg_result = list(submissions.aggregate(pipeline))
        avg_overall = round(avg_result[0]["avg_overall"], 2) if avg_result else 0
        avg_complexity = round(avg_result[0]["avg_complexity"], 2) if avg_result else 0
        avg_coverage = round(avg_result[0]["avg_coverage"], 2) if avg_result else 0
        
        # Stats by language
        pipeline_lang = [
            {"$match": match_query},
            {"$group": {
                "_id": "$language",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$scores.overall"}
            }}
        ]
        
        lang_stats = list(submissions.aggregate(pipeline_lang))
        by_language = {
            stat["_id"]: {
                "count": stat["count"],
                "avg_score": round(stat["avg_score"], 2)
            }
            for stat in lang_stats
        }
        
        # Quality level distribution
        pipeline_quality = [
            {"$match": match_query},
            {"$group": {
                "_id": "$scores.quality_level",
                "count": {"$sum": 1}
            }}
        ]
        
        quality_stats = list(submissions.aggregate(pipeline_quality))
        quality_dist = {stat["_id"]: stat["count"] for stat in quality_stats}
        
        return {
            "total_submissions": total,
            "avg_overall_score": avg_overall,
            "avg_complexity": avg_complexity,
            "avg_coverage": avg_coverage,
            "by_language": by_language,
            "quality_distribution": quality_dist
        }
        
    except Exception as e:
        print(f"Error getting submission stats: {e}")
        return {
            "total_submissions": 0,
            "avg_overall_score": 0,
            "by_language": {},
            "quality_distribution": {}
        }

def get_bug_statistics(filters=None):
    """
    Get bug statistics across all submissions
    Returns:
    - total_bugs: int
    - by_severity: dict (High/Medium/Low counts)
    - by_type: dict (error_type counts)
    - top_bugs: list (most frequent bug descriptions)
    """
    try:
        submissions = get_submissions_collection()
        
        match_query = {}
        if filters:
            if filters.get('language'):
                match_query["language"] = filters['language']
            if filters.get('severity'):
                match_query["bugs.severity"] = filters['severity']
            if filters.get('user'):
                match_query["username"] = filters['user']
            if filters.get('start_date') and filters.get('end_date'):
                match_query["timestamp"] = {
                    "$gte": filters['start_date'],
                    "$lte": filters['end_date']
                }
        
        # Unwind bugs array and get statistics
        pipeline = [
            {"$match": match_query},
            {"$unwind": "$bugs"},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "by_severity": {
                    "$push": "$bugs.severity"
                },
                "by_type": {
                    "$push": "$bugs.error_type"
                },
                "descriptions": {
                    "$push": "$bugs.description_en"
                }
            }}
        ]
        
        result = list(submissions.aggregate(pipeline))
        
        if not result:
            return {
                "total_bugs": 0,
                "by_severity": {},
                "by_type": {},
                "top_bugs": []
            }
        
        data = result[0]
        
        # Count by severity
        severity_counts = {}
        for sev in data.get("by_severity", []):
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        # Count by type
        type_counts = {}
        for typ in data.get("by_type", []):
            type_counts[typ] = type_counts.get(typ, 0) + 1
        
        # Get top 5 most common bugs
        desc_counts = {}
        for desc in data.get("descriptions", []):
            desc_counts[desc] = desc_counts.get(desc, 0) + 1
        
        top_bugs = sorted(desc_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_bugs": data.get("total", 0),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "top_bugs": [{"description": bug[0], "count": bug[1]} for bug in top_bugs]
        }
        
    except Exception as e:
        print(f"Error getting bug statistics: {e}")
        return {
            "total_bugs": 0,
            "by_severity": {},
            "by_type": {},
            "top_bugs": []
        }

def get_recent_submissions(limit=10, filters=None):
    """Get recent submissions with basic info"""
    try:
        submissions = get_submissions_collection()
        
        match_query = {}
        if filters:
            if filters.get('language'):
                match_query["language"] = filters['language']
            if filters.get('user'):
                match_query["username"] = filters['user']
        
        cursor = submissions.find(
            match_query,
            {
                "_id": 1,
                "filename": 1,
                "language": 1,
                "username": 1,
                "timestamp": 1,
                "scores.overall": 1,
                "scores.quality_level": 1
            }
        ).sort("timestamp", -1).limit(limit)
        
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        
        return results
        
    except Exception as e:
        print(f"Error getting recent submissions: {e}")
        return []