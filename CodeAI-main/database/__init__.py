# database/__init__.py
"""
Database package for CodeAI Pakistan
Provides MongoDB connection and query functions
"""

from .db_connector import init_db, get_db, close_db
from .queries import (
    create_user,
    authenticate_user,
    get_user_by_username,
    create_submission,
    get_submissions,
    get_submission_stats,
    get_bug_statistics,
    get_recent_submissions
)

__all__ = [
    'init_db',
    'get_db',
    'close_db',
    'create_user',
    'authenticate_user',
    'get_user_by_username',
    'create_submission',
    'get_submissions',
    'get_submission_stats',
    'get_bug_statistics',
    'get_recent_submissions'
]

