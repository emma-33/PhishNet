"""
GoPhish API Client for PhishNet Backend
Handles communication with GoPhish server
"""
import requests
from typing import Dict, List, Optional


class GoPhishClient:
    """Client for interacting with GoPhish API"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize GoPhish API client
        
        Args:
            base_url: Base URL for GoPhish API (e.g., http://localhost:3333)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def health_check(self) -> bool:
        """
        Check if GoPhish server is accessible
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            response = requests.get(
                f'{self.base_url}/api/campaigns/',
                headers=self.headers,
                timeout=5
            )
            return response.status_code in [200, 401]  # 401 means server is up but auth failed
        except Exception:
            return False
    
    def get_campaigns(self) -> List[Dict]:
        """
        Get all campaigns
        
        Returns:
            List of campaign dictionaries
        """
        response = requests.get(
            f'{self.base_url}/api/campaigns/',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_campaign(self, campaign_id: int) -> Dict:
        """
        Get specific campaign details
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            Campaign dictionary
        """
        response = requests.get(
            f'{self.base_url}/api/campaigns/{campaign_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def create_campaign(self, campaign_data: Dict) -> Dict:
        """
        Create a new campaign
        
        Args:
            campaign_data: Campaign configuration
            
        Returns:
            Created campaign data
        """
        response = requests.post(
            f'{self.base_url}/api/campaigns/',
            json=campaign_data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_groups(self) -> List[Dict]:
        """
        Get all target groups
        
        Returns:
            List of group dictionaries
        """
        response = requests.get(
            f'{self.base_url}/api/groups/',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_templates(self) -> List[Dict]:
        """
        Get all email templates
        
        Returns:
            List of template dictionaries
        """
        response = requests.get(
            f'{self.base_url}/api/templates/',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_landing_pages(self) -> List[Dict]:
        """
        Get all landing pages
        
        Returns:
            List of landing page dictionaries
        """
        response = requests.get(
            f'{self.base_url}/api/pages/',
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
