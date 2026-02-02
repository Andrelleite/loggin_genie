"""
Kibana/Elasticsearch client for fetching logs
"""

from elasticsearch import Elasticsearch
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class KibanaClient:
    """Client for connecting to Elasticsearch/Kibana and fetching logs"""
    
    def __init__(self, elasticsearch_url: str, username: Optional[str] = None,
                 password: Optional[str] = None, api_key: Optional[str] = None,
                 verify_certs: bool = False):
        """
        Initialize Kibana/Elasticsearch client
        
        Args:
            elasticsearch_url: URL of Elasticsearch instance
            username: Basic auth username
            password: Basic auth password
            api_key: API key for authentication
            verify_certs: Verify SSL certificates (default: False)
        """
        
        # Build connection parameters
        params = {
            'hosts': [elasticsearch_url],
            'verify_certs': verify_certs,
        }
        
        # Add authentication
        if api_key:
            params['api_key'] = api_key
        elif username and password:
            params['basic_auth'] = (username, password)
        
        self.es = Elasticsearch(**params)
        
        # Verify connection
        if not self.es.ping():
            raise ConnectionError("Failed to connect to Elasticsearch")
    
    def fetch_logs(self, index: str, query: Optional[Dict] = None, 
                   size: int = 100, sort: Optional[List] = None) -> List[Dict]:
        """
        Fetch logs from Elasticsearch
        
        Args:
            index: Index name or pattern (e.g., 'logs-*')
            query: Elasticsearch query DSL (default: match_all)
            size: Number of logs to fetch (default: 100)
            sort: Sort order (default: timestamp descending)
        
        Returns:
            List of log documents
        """
        
        # Default query: match all
        if query is None:
            query = {"match_all": {}}
        
        # Default sort: timestamp descending
        if sort is None:
            sort = [{"@timestamp": {"order": "desc"}}]
        
        # Build search body
        search_body = {
            "query": query,
            "size": size,
            "sort": sort
        }
        
        try:
            # Execute search
            response = self.es.search(index=index, body=search_body)
            
            # Extract hits
            hits = response['hits']['hits']
            
            return hits
        
        except Exception as e:
            raise Exception(f"Failed to fetch logs: {str(e)}")
    
    def fetch_logs_scroll(self, index: str, query: Optional[Dict] = None,
                          scroll_size: int = 1000, scroll_time: str = '5m') -> List[Dict]:
        """
        Fetch large number of logs using scroll API
        
        Args:
            index: Index name or pattern
            query: Elasticsearch query DSL
            scroll_size: Number of documents per scroll
            scroll_time: Scroll context lifetime (e.g., '5m')
        
        Returns:
            List of all log documents
        """
        
        if query is None:
            query = {"match_all": {}}
        
        all_logs = []
        
        # Initial search
        response = self.es.search(
            index=index,
            body={"query": query},
            scroll=scroll_time,
            size=scroll_size
        )
        
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        all_logs.extend(hits)
        
        # Continue scrolling
        while len(hits) > 0:
            response = self.es.scroll(scroll_id=scroll_id, scroll=scroll_time)
            scroll_id = response['_scroll_id']
            hits = response['hits']['hits']
            all_logs.extend(hits)
        
        # Clear scroll
        self.es.clear_scroll(scroll_id=scroll_id)
        
        return all_logs
    
    def close(self):
        """Close the Elasticsearch connection"""
        self.es.close()
