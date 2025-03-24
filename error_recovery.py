#!/usr/bin/env python3
"""
LogicLens Error Recovery Module

This module provides error handling and recovery mechanisms for the LogicLens application.
It defines error codes, diagnostic tools, and recovery procedures.
"""

import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Error codes and descriptions
ERROR_CODES = {
    # Environment errors (100-199)
    "ENV_001": "Python version incompatible (requires 3.8+)",
    "ENV_002": "Virtual environment creation failed",
    "ENV_003": "Virtual environment activation failed",
    "ENV_004": "Required directory not found",
    "ENV_005": "Insufficient permissions",
    
    # Dependency errors (200-299)
    "DEP_001": "Pip not found in virtual environment",
    "DEP_002": "Dependency installation failed",
    "DEP_003": "Package metadata preparation failed",
    "DEP_004": "Package installation in development mode failed",
    
    # Port/Process errors (300-399)
    "PRC_001": "Port already in use",
    "PRC_002": "Process termination failed",
    "PRC_003": "Flask process not found",
    "PRC_004": "Process launched but terminated unexpectedly",
    
    # Configuration errors (400-499)
    "CFG_001": ".env file creation failed",
    "CFG_002": ".env.example file not found",
    "CFG_003": "Invalid configuration in .env file",
    
    # Application errors (500-599)
    "APP_001": "Flask application failed to start",
    "APP_002": "Test data generation failed",
    "APP_003": "Logging system initialization failed",
    "APP_004": "Database connection failed",
    
    # System errors (900-999)
    "SYS_001": "Insufficient disk space",
    "SYS_002": "Insufficient memory",
    "SYS_003": "Network connectivity issue",
    "SYS_004": "System command execution failed",
    
    # Ollama errors (600-699)
    "OLM_001": "Ollama server not running or unreachable",
    "OLM_002": "Ollama model not found or not available",
    "OLM_003": "Ollama request timeout",
    "OLM_004": "Ollama API error",
    "OLM_005": "Ollama installation issue"
}

class LogicLensError(Exception):
    """Custom exception class for LogicLens application errors"""
    
    def __init__(self, code, message=None, original_exception=None):
        self.code = code
        self.message = message or ERROR_CODES.get(code, "Unknown error")
        self.original_exception = original_exception
        self.timestamp = datetime.now().isoformat()
        super().__init__(f"{code}: {self.message}")


class ErrorHandler:
    """Handles errors and provides recovery mechanisms"""
    
    def __init__(self, config, logger_func=print):
        self.config = config
        self.log = logger_func
        self.recovery_attempted = set()  # Track which recovery methods have been attempted
        
    def handle_error(self, error, context=None):
        """
        Main error handling method.
        
        Args:
            error: The error object (exception or LogicLensError)
            context: Additional context about where the error occurred
            
        Returns:
            bool: True if recovery was successful, False otherwise
        """
        # Convert standard exceptions to LogicLensError
        if not isinstance(error, LogicLensError):
            error = self._map_exception_to_error(error, context)
            
        # Log the error
        self._log_error(error, context)
        
        # Attempt recovery
        return self._attempt_recovery(error, context)
    
    def _map_exception_to_error(self, exception, context=None):
        """Map standard exceptions to LogicLensError with appropriate code"""
        error_code = "SYS_004"  # Default code
        
        if isinstance(exception, FileNotFoundError):
            if context and "pip" in str(exception):
                error_code = "DEP_001"
            elif context and "python" in str(exception):
                error_code = "ENV_001"
            elif context and ".env" in str(exception):
                error_code = "CFG_002"
            else:
                error_code = "ENV_004"
        elif isinstance(exception, PermissionError):
            error_code = "ENV_005"
        elif isinstance(exception, subprocess.SubprocessError):
            if context and "pip install" in context:
                error_code = "DEP_002"
            elif context and "venv" in context:
                error_code = "ENV_002"
            elif context and "flask" in context:
                error_code = "APP_001"
            else:
                error_code = "SYS_004"
        elif isinstance(exception, OSError):
            if context and "socket" in context:
                error_code = "PRC_001"
            elif context and "kill" in context:
                error_code = "PRC_002"
            else:
                error_code = "SYS_004"
        elif str(exception).lower().find("ollama") >= 0 or (context and "ollama" in context.lower()):
            if "connection" in str(exception).lower() or "unreachable" in str(exception).lower():
                error_code = "OLM_001"
            elif "model not found" in str(exception).lower() or "model unavailable" in str(exception).lower():
                error_code = "OLM_002"
            elif "timeout" in str(exception).lower():
                error_code = "OLM_003"
            elif "api" in str(exception).lower():
                error_code = "OLM_004"
            else:
                error_code = "OLM_005"
                
        return LogicLensError(error_code, str(exception), exception)
    
    def _log_error(self, error, context=None):
        """Log detailed error information"""
        self.log(f"ERROR {error.code}: {error.message}", level="ERROR")
        
        if context:
            self.log(f"Context: {context}", level="ERROR")
            
        if error.original_exception:
            self.log(f"Original exception: {error.original_exception.__class__.__name__}: {error.original_exception}", level="ERROR")
            
        # Log system information for certain errors
        if error.code.startswith(("ENV_", "SYS_")):
            self._log_system_diagnostics()
    
    def _log_system_diagnostics(self):
        """Log detailed system diagnostics"""
        self.log("System diagnostics:", level="INFO")
        
        # System info
        self.log(f"  OS: {platform.system()} {platform.release()}", level="INFO")
        self.log(f"  Python: {platform.python_version()}", level="INFO")
        
        # Path info
        self.log(f"  Current directory: {os.getcwd()}", level="INFO")
        self.log(f"  Python executable: {sys.executable}", level="INFO")
        
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        self.log(f"  In virtual environment: {in_venv}", level="INFO")
        
        # Check directories
        backend_dir = Path(self.config["backend_dir"])
        venv_dir = backend_dir / self.config["venv_dir"]
        self.log(f"  Backend directory exists: {backend_dir.exists()}", level="INFO")
        self.log(f"  Virtual environment exists: {venv_dir.exists()}", level="INFO")
        
        # Check disk space
        try:
            if shutil.disk_usage:
                usage = shutil.disk_usage(os.getcwd())
                self.log(f"  Disk space: {usage.free / (1024**3):.2f} GB free", level="INFO")
        except Exception:
            pass
            
        # Check port availability
        port = self.config["flask_port"]
        port_in_use = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            port_in_use = s.connect_ex(('localhost', port)) == 0
        self.log(f"  Port {port} in use: {port_in_use}", level="INFO")
    
    def _attempt_recovery(self, error, context=None):
        """
        Attempt to recover from the error based on its code
        
        Returns:
            bool: True if recovery was successful, False otherwise
        """
        # Skip recovery if we've already tried for this error code
        recovery_key = f"{error.code}_{context or ''}"
        if recovery_key in self.recovery_attempted:
            self.log(f"Recovery already attempted for {error.code} in context '{context}', skipping", level="WARNING")
            return False
            
        self.recovery_attempted.add(recovery_key)
        
        # Dispatch to specific recovery method based on error code
        recovery_method = getattr(self, f"_recover_{error.code.lower()}", None)
        
        if recovery_method:
            self.log(f"Attempting recovery for {error.code}", level="INFO")
            try:
                result = recovery_method(context)
                if result:
                    self.log(f"Recovery successful for {error.code}", level="SUCCESS")
                    return True
                else:
                    self.log(f"Recovery failed for {error.code}", level="ERROR")
                    return False
            except Exception as e:
                self.log(f"Error during recovery attempt: {e}", level="ERROR")
                return False
        else:
            self.log(f"No recovery method available for {error.code}", level="WARNING")
            return False
    
    # Recovery methods for specific error codes
    
    def _recover_dep_001(self, context):
        """Recover from missing pip in virtual environment"""
        # Get paths
        backend_dir = Path(self.config["backend_dir"])
        venv_dir = backend_dir / self.config["venv_dir"]
        
        self.log("Attempting to fix virtual environment by reinstalling it", level="INFO")
        
        # Remove the broken virtual environment
        if venv_dir.exists():
            self.log(f"Removing broken virtual environment at {venv_dir}", level="INFO")
            try:
                shutil.rmtree(venv_dir)
            except Exception as e:
                self.log(f"Failed to remove virtual environment: {e}", level="ERROR")
                return False
        
        # Create a new virtual environment
        self.log("Creating a new virtual environment", level="INFO")
        python_exe = self._find_python_executable()
        if not python_exe:
            return False
            
        try:
            subprocess.run([python_exe, "-m", "venv", str(venv_dir)], check=True)
            
            # Verify pip exists in the new environment
            pip_path = venv_dir / ("Scripts" if platform.system() == "Windows" else "bin") / ("pip.exe" if platform.system() == "Windows" else "pip")
            
            if not pip_path.exists():
                self.log(f"Pip still not found at {pip_path} after recreating virtual environment", level="ERROR")
                return False
                
            self.log("Virtual environment recreated successfully with pip", level="SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to create new virtual environment: {e}", level="ERROR")
            return False
    
    def _recover_env_002(self, context):
        """Recover from virtual environment creation failure"""
        # Try using a different method
        backend_dir = Path(self.config["backend_dir"])
        venv_dir = backend_dir / self.config["venv_dir"]
        
        self.log("Attempting to create virtual environment using alternative method", level="INFO")
        
        # Try using virtualenv if available
        try:
            python_exe = self._find_python_executable()
            if not python_exe:
                return False
                
            # First check if virtualenv is installed
            try:
                subprocess.run([python_exe, "-m", "pip", "install", "virtualenv"], check=True)
                self.log("Installed virtualenv", level="INFO")
            except Exception:
                self.log("Failed to install virtualenv, continuing with standard venv", level="WARNING")
                
            # Try creating with virtualenv
            subprocess.run([python_exe, "-m", "virtualenv", str(venv_dir)], check=True)
            self.log("Virtual environment created successfully with virtualenv", level="SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to create virtual environment with alternative method: {e}", level="ERROR")
            
            # As a last resort, try using the system Python directly
            self.log("Attempting to run without virtual environment", level="WARNING")
            return False
    
    def _recover_prc_001(self, context):
        """Recover from port already in use"""
        port = self.config["flask_port"]
        self.log(f"Attempting to find and stop process using port {port}", level="INFO")
        
        # Find PID using the port
        pid = self._find_pid_by_port(port)
        
        if pid:
            self.log(f"Found process (PID: {pid}) using port {port}", level="INFO")
            
            # Try to terminate the process
            if self._terminate_process(pid):
                # Verify port is now available
                time.sleep(2)  # Give it a moment
                if not self._is_port_in_use(port):
                    self.log(f"Successfully freed port {port}", level="SUCCESS")
                    return True
            
            # If still in use, suggest a different port
            alternate_port = self._find_available_port(start_port=port+1)
            if alternate_port:
                self.log(f"Could not free port {port}. Suggesting alternate port: {alternate_port}", level="SUCCESS")
                # Update the configuration
                self.config["flask_port"] = alternate_port
                return True
        
        return False
    
    def _recover_app_001(self, context):
        """Recover from Flask application startup failure"""
        self.log("Attempting to recover from Flask startup failure", level="INFO")
        
        # Check for common Flask issues
        backend_dir = Path(self.config["backend_dir"])
        
        # Check if the Flask app can be imported
        self.log("Checking if Flask application can be imported", level="INFO")
        
        try:
            # Create a test script to import the Flask app
            test_script = """
import sys
sys.path.insert(0, '.')
try:
    from app import create_app
    app = create_app()
    print("Flask application can be imported successfully")
    sys.exit(0)
except Exception as e:
    print(f"Error importing Flask application: {e}")
    sys.exit(1)
"""
            test_script_path = backend_dir / "test_flask_import.py"
            
            with open(test_script_path, "w") as f:
                f.write(test_script)
                
            # Try running the test script
            venv_python = self._get_venv_python()
            result = subprocess.run([venv_python, str(test_script_path)], 
                                   cwd=str(backend_dir),
                                   capture_output=True,
                                   text=True)
            
            # Clean up
            test_script_path.unlink()
            
            if result.returncode == 0:
                self.log("Flask application can be imported, trying with different host/port", level="INFO")
                # Try with a different port
                self.config["flask_port"] = self._find_available_port()
                # Try with localhost instead of 0.0.0.0
                self.config["flask_host"] = "127.0.0.1"
                self.log(f"Modified configuration: host={self.config['flask_host']}, port={self.config['flask_port']}", level="INFO")
                return True
            else:
                self.log(f"Flask application import failed: {result.stdout} {result.stderr}", level="ERROR")
                return False
                
        except Exception as e:
            self.log(f"Failed to test Flask application import: {e}", level="ERROR")
            return False
    
    def _recover_olm_001(self, context):
        """Recover from Ollama server not running or unreachable"""
        self.log("Attempting to recover from Ollama connection issue", level="INFO")
        
        # Check if Ollama is installed
        ollama_cmd = "ollama" if platform.system() != "Windows" else "ollama.exe"
        
        if not shutil.which(ollama_cmd):
            self.log("Ollama not found in PATH. Attempting to install...", level="INFO")
            try:
                if platform.system() == "Windows":
                    self.log("Please install Ollama manually from: https://ollama.ai/download", level="WARNING")
                    return False
                else:
                    # Try to install Ollama on Unix-like systems
                    self.log("Installing Ollama...", level="INFO")
                    result = subprocess.run(
                        ["curl", "-fsSL", "https://ollama.ai/install.sh"], 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    install_script = result.stdout
                    
                    # Execute the install script
                    subprocess.run(["sh", "-c", install_script], check=True)
                    self.log("Ollama installed successfully", level="SUCCESS")
            except Exception as e:
                self.log(f"Failed to install Ollama: {e}", level="ERROR")
                self.log("Please install Ollama manually from: https://ollama.ai/download", level="WARNING")
                return False
        
        # Try to start Ollama service
        try:
            self.log("Attempting to start Ollama service...", level="INFO")
            
            if platform.system() == "Windows":
                # On Windows, start Ollama in background
                subprocess.Popen([ollama_cmd, "serve"], 
                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            else:
                # On Unix, use nohup to run in background
                subprocess.Popen(["nohup", ollama_cmd, "serve", "&"], 
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                                preexec_fn=os.setpgrp)
            
            # Wait for service to start
            self.log("Waiting for Ollama service to start...", level="INFO")
            time.sleep(5)
            
            # Verify Ollama is running by making a simple request
            ollama_host = self.config["ollama"]["host"]
            try:
                response = subprocess.check_output(["curl", "-s", f"{ollama_host}/api/tags"], text=True)
                if "error" not in response.lower():
                    self.log("Ollama service is now running", level="SUCCESS")
                    return True
            except Exception as e:
                self.log(f"Error verifying Ollama service: {e}", level="ERROR")
                
            return False
        except Exception as e:
            self.log(f"Failed to start Ollama service: {e}", level="ERROR")
            return False
    
    def _recover_olm_002(self, context):
        """Recover from Ollama model not found or not available"""
        self.log("Attempting to recover from missing Ollama model", level="INFO")
        
        # Get the model from config
        model = self.config["ollama"]["model"]
        
        # First ensure Ollama is running
        if not self._check_ollama_running():
            if not self._recover_olm_001(context):
                return False
        
        # Try to pull the model
        try:
            self.log(f"Pulling Ollama model: {model}", level="INFO")
            subprocess.run(["ollama", "pull", model], check=True)
            self.log(f"Successfully pulled model: {model}", level="SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to pull model {model}: {e}", level="ERROR")
            
            # Suggest alternative models
            try:
                self.log("Checking available models...", level="INFO")
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
                available_models = result.stdout.strip()
                
                if available_models:
                    self.log(f"Available models: {available_models}", level="INFO")
                    self.log("Please update your configuration to use one of these models", level="INFO")
                else:
                    self.log("No models available. Please pull a model manually with: ollama pull <model>", level="WARNING")
            except Exception:
                pass
                
            return False
    
    def _check_ollama_running(self):
        """Check if Ollama service is running"""
        ollama_host = self.config["ollama"]["host"]
        try:
            subprocess.check_output(["curl", "-s", "-m", "3", f"{ollama_host}/api/tags"], text=True)
            return True
        except Exception:
            return False
    
    # Utility methods
    
    def _find_python_executable(self):
        """Find an appropriate Python executable (3.8+)"""
        python_cmds = [
            f"python{self.config['python_version']}",
            f"python3.{self.config['python_version'].split('.')[-1]}",
            "python3",
            "python"
        ]
        
        for cmd in python_cmds:
            try:
                output = subprocess.check_output([cmd, "--version"], stderr=subprocess.STDOUT, text=True)
                version_info = output.strip().split()[-1]
                major, minor = map(int, version_info.split(".")[:2])
                if major >= 3 and minor >= 8:  # Ensure Python >= 3.8
                    return cmd
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        self.log("Could not find a suitable Python interpreter (3.8+)", level="ERROR")
        return None
    
    def _get_venv_python(self):
        """Get the path to the Python executable in the virtual environment"""
        backend_dir = Path(self.config["backend_dir"])
        venv_dir = backend_dir / self.config["venv_dir"]
        
        if platform.system() == "Windows":
            return venv_dir / "Scripts" / "python.exe"
        return venv_dir / "bin" / "python"
    
    def _is_port_in_use(self, port):
        """Check if a port is in use"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def _find_available_port(self, start_port=8000, max_attempts=100):
        """Find an available port starting from start_port"""
        port = start_port
        for _ in range(max_attempts):
            if not self._is_port_in_use(port):
                return port
            port += 1
        return None
    
    def _find_pid_by_port(self, port):
        """Find the process ID using a specific port"""
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    ["netstat", "-ano"], text=True
                )
                for line in output.split('\n'):
                    if f":{port}" in line and "LISTENING" in line:
                        return line.strip().split()[-1]
            else:
                if shutil.which("lsof"):
                    output = subprocess.check_output(
                        ["lsof", "-i", f":{port}", "-t"], text=True
                    )
                    return output.strip()
        except subprocess.SubprocessError:
            pass
        return None
    
    def _terminate_process(self, pid):
        """Terminate a process by PID"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True)
            else:
                import signal
                os.kill(int(pid), signal.SIGTERM)
                
                # Give it a moment to terminate
                time.sleep(2)
                
                # Check if it's still running
                try:
                    os.kill(int(pid), 0)  # Signal 0 just checks if process exists
                    # If we get here, the process is still running
                    os.kill(int(pid), signal.SIGKILL)  # Force kill
                except OSError:
                    # Process already stopped
                    pass
                    
            return True
        except Exception as e:
            self.log(f"Failed to terminate process {pid}: {e}", level="ERROR")
            return False


# Self-test function
def self_test():
    """Run a self-test of the error recovery module"""
    # Sample config for testing
    config = {
        "backend_dir": "backend",
        "venv_dir": "venv",
        "python_version": "3.8",
        "flask_port": 5050,
        "flask_host": "0.0.0.0",
    }
    
    def test_logger(msg, level=None):
        print(f"[{level or 'INFO'}] {msg}")
    
    handler = ErrorHandler(config, test_logger)
    
    # Test error mapping
    test_logger("Testing error mapping...", "TEST")
    
    errors = [
        (FileNotFoundError("No such file: venv/bin/pip"), "pip not found"),
        (PermissionError("Permission denied"), "permission error"),
        (subprocess.SubprocessError(), "subprocess error"),
        (OSError("Address already in use"), "socket error"),
    ]
    
    for error, context in errors:
        mapped_error = handler._map_exception_to_error(error, context)
        test_logger(f"Mapped {error.__class__.__name__} to {mapped_error.code}: {mapped_error.message}", "TEST")
    
    # Test system diagnostics
    test_logger("Testing system diagnostics...", "TEST")
    handler._log_system_diagnostics()
    
    # Test recovery methods
    test_logger("Testing recovery methods...", "TEST")
    
    # Mock recovery for DEP_001
    try:
        result = handler._recover_dep_001("test context")
        test_logger(f"DEP_001 recovery test result: {result}", "TEST")
    except Exception as e:
        test_logger(f"DEP_001 recovery test failed: {e}", "TEST")
    
    test_logger("Self-test completed", "TEST")


if __name__ == "__main__":
    self_test() 