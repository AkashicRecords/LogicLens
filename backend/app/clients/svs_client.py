import json
import os
import time
from typing import Dict, List, Optional, Union, Any

import requests

from ..utils.logger import get_logger

class SVSClient:
    """
    Client for integrating with Secure Video Summarizer (SVS)
    
    Enables LogicLens to:
    - Read SVS logs
    - Monitor SVS system health
    - Get test results from SVS
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the SVS client
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.logger = get_logger()
        
        # Set default configuration
        self.api_url = self.config.get("api_url", "http://localhost:8000/api")
        self.api_key = self.config.get("api_key")
        self.timeout = self.config.get("timeout", 10)
        
    def get_logs(self, limit: int = 100, level: Optional[str] = None) -> List[Dict]:
        """
        Get logs from SVS
        
        Args:
            limit: Maximum number of logs to retrieve
            level: Filter by log level (INFO, WARNING, ERROR)
            
        Returns:
            List of log entries
        """
        try:
            params = {"limit": limit}
            if level:
                params["level"] = level
                
            response = requests.get(
                f"{self.api_url}/logs",
                params=params,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("logs", [])
            else:
                self.logger.log_event(
                    component="svs_client",
                    message=f"Failed to get SVS logs: {response.status_code}",
                    level="ERROR",
                    details={"status_code": response.status_code, "response": response.text}
                )
                return []
                
        except Exception as e:
            self.logger.log_event(
                component="svs_client",
                message=f"Exception getting SVS logs: {str(e)}",
                level="ERROR"
            )
            return []
            
    def get_system_health(self) -> Dict:
        """
        Get SVS system health
        
        Returns:
            Health status dictionary
        """
        try:
            response = requests.get(
                f"{self.api_url}/health",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.log_event(
                    component="svs_client",
                    message=f"Failed to get SVS health: {response.status_code}",
                    level="ERROR",
                    details={"status_code": response.status_code, "response": response.text}
                )
                return {"status": "unknown"}
                
        except Exception as e:
            self.logger.log_event(
                component="svs_client",
                message=f"Exception getting SVS health: {str(e)}",
                level="ERROR"
            )
            return {"status": "error", "message": str(e)}
            
    def get_test_results(self, limit: int = 10) -> List[Dict]:
        """
        Get test results from SVS
        
        Args:
            limit: Maximum number of test suites to retrieve
            
        Returns:
            List of test suite results
        """
        try:
            response = requests.get(
                f"{self.api_url}/tests",
                params={"limit": limit},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("test_suites", [])
            else:
                self.logger.log_event(
                    component="svs_client",
                    message=f"Failed to get SVS test results: {response.status_code}",
                    level="ERROR",
                    details={"status_code": response.status_code, "response": response.text}
                )
                return []
                
        except Exception as e:
            self.logger.log_event(
                component="svs_client",
                message=f"Exception getting SVS test results: {str(e)}",
                level="ERROR"
            )
            return []
            
    def import_all_data(self) -> Dict:
        """
        Import all relevant data from SVS
        
        Returns:
            Dictionary with all imported data
        """
        start_time = time.time()
        
        logs = self.get_logs(limit=1000)
        health = self.get_system_health()
        test_results = self.get_test_results()
        
        duration = time.time() - start_time
        
        result = {
            "logs": logs,
            "health": health,
            "test_results": test_results,
            "imported_at": time.time(),
            "duration": duration,
            "counts": {
                "logs": len(logs),
                "test_suites": len(test_results)
            }
        }
        
        self.logger.log_event(
            component="svs_client",
            message=f"Imported data from SVS: {len(logs)} logs, {len(test_results)} test suites",
            level="INFO",
            details={"duration": duration, "health_status": health.get("status")}
        )
        
        return result
            
    def _get_headers(self) -> Dict:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        return headers

# Module-level client instance for easy access
_svs_client = None

def get_svs_client(config: Optional[Dict] = None) -> SVSClient:
    """Get or create SVS client instance"""
    global _svs_client
    if _svs_client is None:
        _svs_client = SVSClient(config)
    return _svs_client 