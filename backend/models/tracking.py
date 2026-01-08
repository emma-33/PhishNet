"""
Data models for PhishNet Backend
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any


class PageVisit:
    """Model for tracking page visits"""
    
    def __init__(self, campaign_id: Optional[str], user_identifier: Optional[str],
                 ip_address: str, user_agent: str, page_url: str,
                 visit_id: Optional[int] = None, 
                 visit_timestamp: Optional[datetime] = None):
        self.id = visit_id
        self.campaign_id = campaign_id
        self.user_identifier = user_identifier
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.page_url = page_url
        self.visit_timestamp = visit_timestamp or datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'user_identifier': self.user_identifier,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'page_url': self.page_url,
            'visit_timestamp': self.visit_timestamp.isoformat() if self.visit_timestamp else None
        }
    
    @staticmethod
    def create(db, campaign_id: Optional[str], user_identifier: Optional[str],
               ip_address: str, user_agent: str, page_url: str) -> int:
        """
        Create a new page visit record
        
        Returns:
            ID of created record
        """
        query = """
        INSERT INTO page_visits 
        (campaign_id, user_identifier, ip_address, user_agent, page_url)
        VALUES (?, ?, ?, ?, ?)
        """
        cursor = db.execute(query, (campaign_id, user_identifier, ip_address, 
                                     user_agent, page_url))
        return cursor.lastrowid
    
    @staticmethod
    def get_by_campaign(db, campaign_id: str):
        """Get all visits for a campaign"""
        query = """
        SELECT * FROM page_visits 
        WHERE campaign_id = ?
        ORDER BY visit_timestamp DESC
        """
        return db.fetchall(query, (campaign_id,))


class FormSubmission:
    """Model for tracking form submissions"""
    
    def __init__(self, campaign_id: Optional[str], user_identifier: Optional[str],
                 ip_address: str, user_agent: str, page_url: str,
                 username: Optional[str] = None, password: Optional[str] = None,
                 additional_data: Optional[str] = None,
                 submission_id: Optional[int] = None,
                 submission_timestamp: Optional[datetime] = None):
        self.id = submission_id
        self.campaign_id = campaign_id
        self.user_identifier = user_identifier
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.page_url = page_url
        self.username = username
        self.password = password
        self.additional_data = additional_data
        self.submission_timestamp = submission_timestamp or datetime.now(timezone.utc)
    
    def to_dict(self, mask_password: bool = True) -> Dict[str, Any]:
        """Convert to dictionary (password masked by default)"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'user_identifier': self.user_identifier,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'page_url': self.page_url,
            'username': self.username,
            'password': '***' if (mask_password and self.password) else self.password,
            'additional_data': self.additional_data,
            'submission_timestamp': self.submission_timestamp.isoformat() if self.submission_timestamp else None
        }
    
    @staticmethod
    def create(db, campaign_id: Optional[str], user_identifier: Optional[str],
               ip_address: str, user_agent: str, page_url: str,
               username: Optional[str] = None, password: Optional[str] = None,
               additional_data: Optional[str] = None) -> int:
        """
        Create a new form submission record
        
        Returns:
            ID of created record
        """
        query = """
        INSERT INTO form_submissions 
        (campaign_id, user_identifier, ip_address, user_agent, page_url, 
         username, password, additional_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = db.execute(query, (campaign_id, user_identifier, ip_address,
                                     user_agent, page_url, username, password,
                                     additional_data))
        return cursor.lastrowid
    
    @staticmethod
    def get_by_campaign(db, campaign_id: str):
        """Get all submissions for a campaign"""
        query = """
        SELECT * FROM form_submissions 
        WHERE campaign_id = ?
        ORDER BY submission_timestamp DESC
        """
        return db.fetchall(query, (campaign_id,))
