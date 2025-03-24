import json
import os
import platform
import socket
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

import psutil

from .logger import get_logger

class MonitoringManager:
    """
    System and application monitoring utility for collecting metrics,
    generating alerts, and tracking performance.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the monitoring manager
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.logger = get_logger()
        self.initialized = False
        self.metrics_history = []
        self.max_history_size = self.config.get("max_history_size", 1000)
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        self.alert_cooldown = {}  # Track when alerts were last sent
        
    def initialize(self, config: Optional[Dict] = None) -> bool:
        """
        Initialize the monitoring system
        
        Args:
            config: Configuration to apply (updates existing config)
            
        Returns:
            True if initialization was successful
        """
        if config:
            self.config.update(config)
            
        # Set up storage
        self.storage_dir = self.config.get("storage_dir", "monitoring_data")
        if self.config.get("persist_metrics", False):
            os.makedirs(self.storage_dir, exist_ok=True)
            
        # Basic system info
        self.system_info = {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total
        }
        
        self.logger.log_event(
            component="monitoring",
            message="Monitoring system initialized",
            level="INFO",
            details=self.system_info
        )
        
        self.initialized = True
        return True
        
    def collect_metrics(self) -> Dict:
        """
        Collect current system metrics
        
        Returns:
            Dictionary of metrics
        """
        if not self.initialized:
            self.initialize()
            
        # Collect metrics
        current_time = datetime.now()
        
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            metrics = {
                "timestamp": current_time.isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used": memory.used,
                    "memory_available": memory.available,
                    "disk_percent": disk.percent,
                    "disk_used": disk.used,
                    "disk_free": disk.free,
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv
                },
                "application": self._collect_application_metrics()
            }
            
            # Store metrics history
            self.metrics_history.append(metrics)
            
            # Trim history if needed
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history = self.metrics_history[-self.max_history_size:]
                
            # Check for alerts
            self._check_alerts(metrics)
            
            # Persist metrics if configured
            if self.config.get("persist_metrics", False) and \
               current_time.second % self.config.get("persist_interval", 60) == 0:
                self._persist_metrics(metrics)
                
            return metrics
            
        except Exception as e:
            self.logger.log_event(
                component="monitoring",
                message=f"Failed to collect metrics: {str(e)}",
                level="ERROR"
            )
            return {
                "timestamp": current_time.isoformat(),
                "error": str(e)
            }
            
    def _collect_application_metrics(self) -> Dict:
        """Collect application-specific metrics"""
        # Default implementation collects process metrics
        process = psutil.Process(os.getpid())
        
        return {
            "process_cpu_percent": process.cpu_percent(interval=0.1),
            "process_memory_percent": process.memory_percent(),
            "process_memory_rss": process.memory_info().rss,
            "process_threads": process.num_threads(),
            "process_connections": len(process.connections())
        }
    
    def _check_alerts(self, metrics: Dict) -> None:
        """Check metrics against alert thresholds"""
        current_time = time.time()
        
        # CPU alert
        cpu_threshold = self.alert_thresholds.get("cpu_percent", 90)
        if metrics["system"]["cpu_percent"] > cpu_threshold:
            if "cpu" not in self.alert_cooldown or \
               current_time - self.alert_cooldown.get("cpu", 0) > self.config.get("alert_cooldown_seconds", 300):
                self.logger.log_event(
                    component="monitoring",
                    message=f"HIGH CPU USAGE: {metrics['system']['cpu_percent']}% exceeds threshold of {cpu_threshold}%",
                    level="WARNING",
                    details={"metric": "cpu_percent", "value": metrics["system"]["cpu_percent"]}
                )
                self.alert_cooldown["cpu"] = current_time
        
        # Memory alert
        memory_threshold = self.alert_thresholds.get("memory_percent", 90)
        if metrics["system"]["memory_percent"] > memory_threshold:
            if "memory" not in self.alert_cooldown or \
               current_time - self.alert_cooldown.get("memory", 0) > self.config.get("alert_cooldown_seconds", 300):
                self.logger.log_event(
                    component="monitoring",
                    message=f"HIGH MEMORY USAGE: {metrics['system']['memory_percent']}% exceeds threshold of {memory_threshold}%",
                    level="WARNING",
                    details={"metric": "memory_percent", "value": metrics["system"]["memory_percent"]}
                )
                self.alert_cooldown["memory"] = current_time
        
        # Disk alert
        disk_threshold = self.alert_thresholds.get("disk_percent", 90)
        if metrics["system"]["disk_percent"] > disk_threshold:
            if "disk" not in self.alert_cooldown or \
               current_time - self.alert_cooldown.get("disk", 0) > self.config.get("alert_cooldown_seconds", 300):
                self.logger.log_event(
                    component="monitoring",
                    message=f"HIGH DISK USAGE: {metrics['system']['disk_percent']}% exceeds threshold of {disk_threshold}%",
                    level="WARNING",
                    details={"metric": "disk_percent", "value": metrics["system"]["disk_percent"]}
                )
                self.alert_cooldown["disk"] = current_time
    
    def _persist_metrics(self, metrics: Dict) -> None:
        """Persist metrics to storage"""
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"metrics_{date_str}.jsonl"
            filepath = os.path.join(self.storage_dir, filename)
            
            with open(filepath, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
                
        except Exception as e:
            self.logger.log_event(
                component="monitoring",
                message=f"Failed to persist metrics: {str(e)}",
                level="ERROR"
            )
    
    def get_metrics_history(self, count: int = 60) -> List[Dict]:
        """
        Get metrics history
        
        Args:
            count: Number of most recent metrics to return
            
        Returns:
            List of metrics dictionaries
        """
        return self.metrics_history[-count:]
    
    def get_system_info(self) -> Dict:
        """
        Get basic system information
        
        Returns:
            Dictionary of system info
        """
        if not self.initialized:
            self.initialize()
            
        return self.system_info
    
    def analyze_trends(self, metric_name: str, window: int = 60) -> Dict:
        """
        Analyze trends for a specific metric
        
        Args:
            metric_name: Name of the metric to analyze (e.g., 'system.cpu_percent')
            window: Number of data points to include
            
        Returns:
            Trend analysis
        """
        if not self.metrics_history:
            return {"error": "No metrics data available"}
            
        # Extract metric values
        values = []
        parts = metric_name.split('.')
        
        for metric in self.metrics_history[-window:]:
            try:
                value = metric
                for part in parts:
                    value = value[part]
                values.append(value)
            except (KeyError, TypeError):
                continue
                
        if not values:
            return {"error": f"Metric {metric_name} not found"}
            
        # Calculate statistics
        avg = sum(values) / len(values)
        minimum = min(values)
        maximum = max(values)
        
        # Calculate trend (positive = increasing, negative = decreasing)
        if len(values) >= 2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            trend = second_avg - first_avg
        else:
            trend = 0
            
        return {
            "metric": metric_name,
            "count": len(values),
            "min": minimum,
            "max": maximum,
            "avg": avg,
            "trend": trend,
            "trend_percent": (trend / avg * 100) if avg != 0 else 0
        }

# Global instance
_monitoring_manager = None

def get_monitoring_manager(config: Optional[Dict] = None) -> MonitoringManager:
    """Get or create the monitoring manager instance"""
    global _monitoring_manager
    if _monitoring_manager is None:
        _monitoring_manager = MonitoringManager(config)
    return _monitoring_manager 