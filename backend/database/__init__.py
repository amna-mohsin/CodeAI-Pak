"""
Database package for CodeAI Pakistan
Provides MongoDB connection and query utilities
"""

from .db_connector import init_db, get_db
from .queries import (
    create_user,
    authenticate_user,
    get_user_by_username,
    get_user_by_id,
    update_last_login,
    update_last_visit,
    create_submission,
    get_submissions,
    get_submission_by_id,
    get_submission_stats,
    get_bug_statistics,
    get_recent_submissions
)

__all__ = [
    'init_db',
    'get_db',
    'create_user',
    'authenticate_user',
    'get_user_by_username',
    'get_user_by_id',
    'update_last_login',
    'update_last_visit',
    'create_submission',
    'get_submissions',
    'get_submission_by_id',
    'get_submission_stats',
    'get_bug_statistics',
    'get_recent_submissions'
]