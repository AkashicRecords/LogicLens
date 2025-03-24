import json
import os
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from .logger import get_logger

class TestManager:
    """
    Test result management system for tracking test execution, results,
    and generating insights about test performance.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the test manager
        
        Args:
            config: Configuration options for the test manager
        """
        self.config = config or {}
        self.logger = get_logger()
        
        # Initialize data structures
        self.test_suites = {}
        self.active_suites = set()
        self.storage_dir = self.config.get("storage_dir", "test_results")
        
        # Create storage directory if it doesn't exist
        if self.config.get("persist_results", False):
            os.makedirs(self.storage_dir, exist_ok=True)
    
    def start_suite(self, suite_id: Optional[str] = None, name: str = "Test Suite") -> str:
        """
        Start a new test suite
        
        Args:
            suite_id: Optional unique identifier for the suite (generated if not provided)
            name: Name of the test suite
            
        Returns:
            The suite_id for the created suite
        """
        # Generate ID if not provided
        if suite_id is None:
            suite_id = str(uuid.uuid4())
            
        # Create suite record
        self.test_suites[suite_id] = {
            "id": suite_id,
            "name": name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "status": "RUNNING",
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0
            }
        }
        
        self.active_suites.add(suite_id)
        
        # Log suite start
        self.logger.log_event(
            component="test_manager",
            message=f"Started test suite: {name}",
            level="INFO",
            details={"suite_id": suite_id}
        )
        
        return suite_id
    
    def add_test_result(self, 
                       suite_id: str, 
                       test_id: str, 
                       test_name: str, 
                       status: str, 
                       duration: float,
                       message: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> Dict:
        """
        Add a test result to a suite
        
        Args:
            suite_id: ID of the test suite
            test_id: Unique identifier for the test
            test_name: Name of the test
            status: Status of the test (PASSED, FAILED, SKIPPED)
            duration: Duration of the test in seconds
            message: Optional message, especially useful for failures
            metadata: Additional metadata about the test
            
        Returns:
            The test result entry
        """
        if suite_id not in self.test_suites:
            raise ValueError(f"Test suite with ID {suite_id} does not exist")
            
        # Normalize status
        status = status.upper()
        if status not in ["PASSED", "FAILED", "SKIPPED"]:
            status = "UNKNOWN"
            
        # Create test result
        test_result = {
            "id": test_id,
            "name": test_name,
            "status": status,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "metadata": metadata or {}
        }
        
        # Add to suite
        self.test_suites[suite_id]["tests"].append(test_result)
        
        # Update summary
        summary = self.test_suites[suite_id]["summary"]
        summary["total"] += 1
        if status == "PASSED":
            summary["passed"] += 1
        elif status == "FAILED":
            summary["failed"] += 1
        elif status == "SKIPPED":
            summary["skipped"] += 1
        summary["duration"] += duration
        
        # Log test result
        level = "INFO" if status == "PASSED" else "WARNING" if status == "SKIPPED" else "ERROR"
        self.logger.log_event(
            component="test_manager",
            message=f"Test {test_name}: {status}" + (f" - {message}" if message else ""),
            level=level,
            details={
                "suite_id": suite_id,
                "test_id": test_id,
                "duration": duration,
                "metadata": metadata
            }
        )
        
        return test_result
    
    def end_suite(self, suite_id: str, status: Optional[str] = None) -> Dict:
        """
        End a test suite and finalize results
        
        Args:
            suite_id: ID of the test suite
            status: Override the calculated status
            
        Returns:
            The complete test suite data
        """
        if suite_id not in self.test_suites:
            raise ValueError(f"Test suite with ID {suite_id} does not exist")
            
        if suite_id not in self.active_suites:
            return self.test_suites[suite_id]  # Already ended
            
        # Mark end time
        self.test_suites[suite_id]["end_time"] = datetime.now().isoformat()
        
        # Calculate status if not provided
        if status is None:
            summary = self.test_suites[suite_id]["summary"]
            if summary["failed"] > 0:
                status = "FAILED"
            elif summary["total"] == 0:
                status = "EMPTY"
            else:
                status = "PASSED"
                
        self.test_suites[suite_id]["status"] = status
        
        # Remove from active suites
        self.active_suites.remove(suite_id)
        
        # Log suite completion
        self.logger.log_event(
            component="test_manager",
            message=f"Completed test suite: {self.test_suites[suite_id]['name']} - {status}",
            level="INFO" if status == "PASSED" else "ERROR",
            details={
                "suite_id": suite_id,
                "summary": self.test_suites[suite_id]["summary"]
            }
        )
        
        # Persist results if configured
        if self.config.get("persist_results", False):
            self._persist_results(suite_id)
            
        return self.test_suites[suite_id]
    
    def _persist_results(self, suite_id: str) -> None:
        """Persist test results to storage"""
        try:
            suite_data = self.test_suites[suite_id]
            filename = f"{suite_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.storage_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(suite_data, f, indent=2)
                
            self.logger.log_event(
                component="test_manager",
                message=f"Persisted test results to {filepath}",
                level="DEBUG"
            )
        except Exception as e:
            self.logger.log_event(
                component="test_manager",
                message=f"Failed to persist test results: {str(e)}",
                level="ERROR"
            )
    
    def get_suite(self, suite_id: str) -> Optional[Dict]:
        """
        Get test suite data by ID
        
        Args:
            suite_id: ID of the test suite
            
        Returns:
            Test suite data or None if not found
        """
        return self.test_suites.get(suite_id)
    
    def get_all_suites(self) -> List[Dict]:
        """
        Get all test suites
        
        Returns:
            List of all test suites
        """
        return list(self.test_suites.values())
    
    def import_junit_xml(self, file_path: str, suite_name: Optional[str] = None) -> str:
        """
        Import test results from JUnit XML format
        
        Args:
            file_path: Path to JUnit XML file
            suite_name: Optional name for the test suite
            
        Returns:
            The created suite_id
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Determine suite name
            if suite_name is None:
                suite_name = os.path.basename(file_path).split('.')[0]
                
            # Create new suite
            suite_id = self.start_suite(name=suite_name)
            
            # Parse testsuites/testsuite/testcase elements
            if root.tag == 'testsuites':
                testsuites = root.findall('./testsuite')
            else:  # Assume it's a single testsuite
                testsuites = [root]
                
            for testsuite in testsuites:
                for testcase in testsuite.findall('./testcase'):
                    test_name = testcase.get('name', 'Unknown Test')
                    test_id = f"{testsuite.get('name', 'suite')}_{test_name}"
                    
                    # Get duration
                    duration = float(testcase.get('time', 0))
                    
                    # Determine status and message
                    failure = testcase.find('./failure')
                    error = testcase.find('./error')
                    skipped = testcase.find('./skipped')
                    
                    if failure is not None:
                        status = "FAILED"
                        message = failure.get('message', failure.text)
                    elif error is not None:
                        status = "FAILED"
                        message = error.get('message', error.text)
                    elif skipped is not None:
                        status = "SKIPPED"
                        message = skipped.get('message', skipped.text)
                    else:
                        status = "PASSED"
                        message = None
                        
                    # Add test result
                    self.add_test_result(
                        suite_id=suite_id,
                        test_id=test_id,
                        test_name=test_name,
                        status=status,
                        duration=duration,
                        message=message,
                        metadata={
                            "classname": testcase.get('classname'),
                            "file": testcase.get('file')
                        }
                    )
            
            # End suite
            self.end_suite(suite_id)
            return suite_id
            
        except Exception as e:
            self.logger.log_event(
                component="test_manager",
                message=f"Failed to import JUnit XML: {str(e)}",
                level="ERROR"
            )
            raise

# Provide singleton-like access
_test_manager = None

def get_test_manager(config: Optional[Dict] = None) -> TestManager:
    """Get or create test manager instance"""
    global _test_manager
    if _test_manager is None:
        _test_manager = TestManager(config)
    return _test_manager 