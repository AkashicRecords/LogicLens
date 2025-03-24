import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union

class AILogger:
    """
    Advanced logging utility for AI applications with structured output
    and multi-destination support.
    """
    
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    def __init__(self, app_name: str = "logiclens", config: Optional[Dict] = None):
        """
        Initialize the logger with configuration
        
        Args:
            app_name: Name of the application
            config: Configuration dictionary with options
        """
        self.app_name = app_name
        self.config = config or {}
        
        # Set up Python's standard logging
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if configured
        log_file = self.config.get("log_file")
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        # Initialize storage for logs if needed
        self.logs_storage = []
        self.store_logs = self.config.get("store_logs", False)
    
    def log_event(self, component: str, message: str, level: str = "INFO", details: Optional[Dict] = None) -> Dict:
        """
        Log an event with structured data
        
        Args:
            component: Component generating the log
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            details: Additional structured data for the log
            
        Returns:
            Log entry as dictionary
        """
        if level not in self.LEVELS:
            level = "INFO"
            
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "app": self.app_name,
            "component": component,
            "message": message,
            "level": level,
            "details": details or {}
        }
        
        # Log using standard logging
        self.logger.log(
            self.LEVELS[level], 
            f"[{component}] {message}" + (f" | {json.dumps(details)}" if details else "")
        )
        
        # Store if configured
        if self.store_logs:
            self.logs_storage.append(log_entry)
            
        # Send to external services if configured
        self._send_to_external_services(log_entry)
            
        return log_entry
    
    def _send_to_external_services(self, log_entry: Dict) -> None:
        """Send log to configured external services"""
        # Example: Send to remote API
        api_url = self.config.get("api_url")
        api_key = self.config.get("api_key")
        
        if api_url and api_key and log_entry["level"] != "DEBUG":
            try:
                import requests
                requests.post(
                    api_url + "/api/logs",
                    json=log_entry,
                    headers={"X-API-Key": api_key},
                    timeout=1  # Non-blocking
                )
            except Exception as e:
                self.logger.error(f"Failed to send log to external API: {e}")
    
    def get_logs(self, 
                filter_component: Optional[str] = None, 
                filter_level: Optional[str] = None, 
                limit: int = 100) -> list:
        """
        Get stored logs with optional filtering
        
        Args:
            filter_component: Filter logs by component
            filter_level: Filter logs by level
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        if not self.store_logs:
            return []
            
        filtered_logs = self.logs_storage
        
        if filter_component:
            filtered_logs = [log for log in filtered_logs if log["component"] == filter_component]
            
        if filter_level:
            filtered_logs = [log for log in filtered_logs if log["level"] == filter_level]
            
        # Sort by timestamp (newest first) and limit
        return sorted(filtered_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def read_external_logs(self, file_path: str, format_type: str = "json") -> list:
        """
        Read logs from external file
        
        Args:
            file_path: Path to log file
            format_type: Format of log file (json, jsonl, text)
            
        Returns:
            List of log entries
        """
        if not os.path.exists(file_path):
            self.logger.error(f"Log file does not exist: {file_path}")
            return []
            
        logs = []
        try:
            with open(file_path, 'r') as f:
                if format_type == "json":
                    logs = json.load(f)
                elif format_type == "jsonl":
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))
                elif format_type == "text":
                    # Simple text parsing - assumes format: "[LEVEL] Component: Message"
                    for line in f:
                        parts = line.strip().split(" ", 1)
                        if len(parts) >= 2 and parts[0].startswith('[') and parts[0].endswith(']'):
                            level = parts[0][1:-1]
                            rest = parts[1]
                            component_parts = rest.split(":", 1)
                            if len(component_parts) >= 2:
                                component = component_parts[0].strip()
                                message = component_parts[1].strip()
                                logs.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "component": component,
                                    "message": message,
                                    "level": level,
                                    "details": {}
                                })
            return logs
        except Exception as e:
            self.logger.error(f"Failed to read log file: {e}")
            return []

# Convenience functions for direct usage
_default_logger = None

def get_logger(app_name: str = "logiclens", config: Optional[Dict] = None) -> AILogger:
    """Get or create the default logger instance"""
    global _default_logger
    if _default_logger is None:
        _default_logger = AILogger(app_name, config)
    return _default_logger

def log(component: str, message: str, level: str = "INFO", details: Optional[Dict] = None) -> Dict:
    """Log an event using the default logger"""
    return get_logger().log_event(component, message, level, details) 