#!/usr/bin/env python3
"""
LogicLens Application Manager

A unified, cross-platform script to manage the LogicLens application lifecycle:
- Creating and managing virtual environments
- Installing dependencies
- Starting/stopping the application
- Generating test data
- Environment health checks

Usage: python logiclens_manage.py [command]
Commands:
  start         Start the LogicLens application with proper environment setup
  stop          Stop any running LogicLens instances
  setup         Set up the environment without starting the application
  test          Generate test data for the application
  status        Check status of LogicLens and environment
"""

import argparse
import datetime
import importlib.util
import json
import os
import platform
import random
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

# Import error recovery module if available
try:
    from error_recovery import ErrorHandler, LogicLensError
    HAS_ERROR_HANDLER = True
except ImportError:
    HAS_ERROR_HANDLER = False

# Configuration
CONFIG = {
    "backend_dir": "backend",
    "venv_dir": "venv",
    "python_version": "3.8",
    "flask_port": 5050,
    "flask_host": "0.0.0.0",
    "debug_mode": True,
    "requirements_file": "requirements.txt",
    "log_colors": {
        "INFO": "\033[94m",  # Blue
        "SUCCESS": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "END": "\033[0m"  # Reset
    },
    # Ollama configuration
    "ollama": {
        "host": "http://localhost:11434",
        "model": "llama2",
        "enabled": True,
        "timeout": 30,
        "verify_on_startup": True
    }
}

# Handle Windows color support
if platform.system() == "Windows":
    # Enable color support for Windows console
    try:
        import colorama
        colorama.init()
    except ImportError:
        # Fallback to no colors on Windows if colorama isn't available
        for key in CONFIG["log_colors"]:
            CONFIG["log_colors"][key] = ""


def log(message, level="INFO", end="\n"):
    """Print a colored log message based on level."""
    prefix = {
        "INFO": "[LOGICLENS]",
        "SUCCESS": "[LOGICLENS]",
        "WARNING": "[WARNING]",
        "ERROR": "[ERROR]"
    }.get(level, "[LOGICLENS]")
    
    color = CONFIG["log_colors"].get(level, "")
    end_color = CONFIG["log_colors"]["END"] if color else ""
    
    print(f"{color}{prefix} {message}{end_color}", end=end)
    sys.stdout.flush()


# Initialize error handler if available
ERROR_HANDLER = None
if HAS_ERROR_HANDLER:
    ERROR_HANDLER = ErrorHandler(CONFIG, log)
    log("Error recovery system initialized", level="INFO")


def log_system_diagnostics():
    """Log detailed system diagnostics when error handler is not available"""
    log("System diagnostics:", level="INFO")
    
    # System info
    log(f"  OS: {platform.system()} {platform.release()}", level="INFO")
    log(f"  Python: {platform.python_version()}", level="INFO")
    
    # Path info
    log(f"  Current directory: {os.getcwd()}", level="INFO")
    log(f"  Python executable: {sys.executable}", level="INFO")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    log(f"  In virtual environment: {in_venv}", level="INFO")
    
    # Check directories
    backend_dir = Path(CONFIG["backend_dir"])
    venv_dir = backend_dir / CONFIG["venv_dir"]
    log(f"  Backend directory exists: {backend_dir.exists()}", level="INFO")
    log(f"  Virtual environment exists: {venv_dir.exists()}", level="INFO")
    
    # Check disk space
    try:
        if shutil.disk_usage:
            usage = shutil.disk_usage(os.getcwd())
            log(f"  Disk space: {usage.free / (1024**3):.2f} GB free", level="INFO")
    except Exception:
        pass
        
    # Check port availability
    port = CONFIG["flask_port"]
    port_in_use = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        port_in_use = s.connect_ex(('localhost', port)) == 0
    log(f"  Port {port} in use: {port_in_use}", level="INFO")


def get_python_executable():
    """Get the appropriate Python executable for the environment."""
    # If within virtual environment, use the venv's python
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable
    
    # Otherwise try to find the correct Python version
    python_cmds = [
        f"python{CONFIG['python_version']}",
        f"python3.{CONFIG['python_version'].split('.')[-1]}",
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
    
    log("Could not find a suitable Python interpreter (3.8+)", level="ERROR")
    sys.exit(1)


def is_venv_activated():
    """Check if a virtual environment is activated."""
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))


def create_or_update_venv():
    """Create or update the virtual environment."""
    backend_dir = Path(CONFIG["backend_dir"])
    venv_dir = backend_dir / CONFIG["venv_dir"]
    
    # Check if venv already exists
    if venv_dir.exists():
        log(f"Virtual environment already exists at {venv_dir}")
        return venv_dir
    
    # Create virtual environment
    log(f"Creating virtual environment with Python {CONFIG['python_version']}...")
    python_exe = get_python_executable()
    
    try:
        subprocess.run([python_exe, "-m", "venv", str(venv_dir)], check=True)
        log("Virtual environment created successfully", level="SUCCESS")
        return venv_dir
    except subprocess.SubprocessError as e:
        if ERROR_HANDLER:
            # Attempt recovery with error handler
            error = LogicLensError("ENV_002", str(e), e)
            if ERROR_HANDLER.handle_error(error, context="Creating virtual environment"):
                # If recovery was successful, try again or return the recovery result
                if venv_dir.exists():
                    log("Virtual environment recovered after initial failure", level="SUCCESS")
                    return venv_dir
                return create_or_update_venv()  # Try again after recovery
        
        # If no error handler or recovery failed
        log(f"Failed to create virtual environment: {e}", level="ERROR")
        sys.exit(1)


def get_venv_python(venv_dir):
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return Path(venv_dir) / "Scripts" / "python.exe"
    return Path(venv_dir) / "bin" / "python"


def get_venv_pip(venv_dir):
    """Get the path to the pip executable in the virtual environment."""
    if platform.system() == "Windows":
        return Path(venv_dir) / "Scripts" / "pip.exe"
    return Path(venv_dir) / "bin" / "pip"


def activate_venv(venv_dir):
    """
    Activate the virtual environment programmatically.
    
    Note: This doesn't modify the current process environment fully like source/activate would.
    It only updates PATH and the Python module search path for imports to work.
    """
    venv_dir = Path(venv_dir)
    
    if is_venv_activated():
        log("Virtual environment is already activated")
        return True
    
    # Add the venv's bin/Scripts directory to PATH
    if platform.system() == "Windows":
        bin_dir = venv_dir / "Scripts"
    else:
        bin_dir = venv_dir / "bin"
    
    if not bin_dir.exists():
        log(f"Virtual environment bin directory not found at {bin_dir}", level="ERROR")
        return False
    
    # Update PATH
    os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ['PATH']}"
    
    # Modify Python's path to include the virtual environment
    sys.path.insert(0, str(bin_dir))
    
    # Set VIRTUAL_ENV environment variable
    os.environ["VIRTUAL_ENV"] = str(venv_dir)
    
    log(f"Virtual environment at {venv_dir} activated")
    return True


def install_dependencies(venv_dir):
    """Install dependencies in the virtual environment."""
    pip = get_venv_pip(venv_dir)
    backend_dir = Path(CONFIG["backend_dir"])
    requirements_file = backend_dir / CONFIG["requirements_file"]
    
    if requirements_file.exists():
        log(f"Installing requirements from {requirements_file}...")
        try:
            subprocess.run([str(pip), "install", "-r", str(requirements_file)], check=True)
            log("Dependencies installed successfully", level="SUCCESS")
        except subprocess.SubprocessError as e:
            if ERROR_HANDLER:
                # Attempt recovery with error handler
                error = LogicLensError("DEP_002", str(e), e)
                if ERROR_HANDLER.handle_error(error, context="Installing requirements"):
                    # If recovery was successful, try again
                    return install_dependencies(venv_dir)
            
            # If no error handler or recovery failed
            log(f"Failed to install dependencies: {e}", level="ERROR")
            return False
    else:
        log(f"Installing package in development mode...")
        try:
            subprocess.run([str(pip), "install", "-e", "."], cwd=str(backend_dir.parent), check=True)
            log("Package installed in development mode", level="SUCCESS")
        except subprocess.SubprocessError as e:
            if ERROR_HANDLER:
                # Attempt recovery with error handler
                error = LogicLensError("DEP_004", str(e), e)
                if ERROR_HANDLER.handle_error(error, context="Installing package in dev mode"):
                    # If recovery was successful, try again
                    return install_dependencies(venv_dir)
            
            # If no error handler or recovery failed
            log(f"Failed to install package: {e}", level="ERROR")
            return False
    
    return True


def setup_env_file():
    """Set up the .env file if it doesn't exist."""
    backend_dir = Path(CONFIG["backend_dir"])
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if env_file.exists():
        log(".env file already exists")
        return True
    
    if env_example.exists():
        log("Creating .env file from example...")
        try:
            shutil.copy(env_example, env_file)
            log(".env file created", level="SUCCESS")
            log("You may want to review and update the .env file with your configuration", level="WARNING")
            return True
        except Exception as e:
            log(f"Failed to create .env file: {e}", level="ERROR")
            return False
    else:
        log(".env.example file not found", level="WARNING")
        return False


def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_pid_by_port(port):
    """Find the process ID using a specific port."""
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(
                ["netstat", "-ano", "|", "findstr", f":{port}"], text=True, shell=True
            )
            for line in output.strip().split('\n'):
                if 'LISTENING' in line:
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


def find_flask_processes():
    """Find all Flask/LogicLens processes."""
    pids = []
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(
                ["tasklist", "/fi", "imagename eq python.exe", "/fo", "csv", "/nh"], text=True
            )
            for line in output.strip().split('\n'):
                if "flask" in line.lower() or "logiclens" in line.lower():
                    if line.strip():
                        pid = line.strip().split(",")[1].strip('"')
                        pids.append(pid)
        else:
            output = subprocess.check_output(
                ["ps", "aux"], text=True
            )
            for line in output.strip().split('\n'):
                if "flask run" in line or "logiclens" in line:
                    if "grep" not in line and line.strip():
                        pid = line.strip().split()[1]
                        pids.append(pid)
    except subprocess.SubprocessError:
        pass
    return pids


def stop_process(pid):
    """Stop a process by its PID."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=True)
        else:
            # Try SIGTERM first for graceful shutdown
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
        log(f"Failed to stop process {pid}: {e}", level="ERROR")
        return False


def stop_application():
    """Stop any running LogicLens instances."""
    log("Stopping any running LogicLens instances...")
    
    # First check the configured port
    if is_port_in_use(CONFIG["flask_port"]):
        port_pid = find_pid_by_port(CONFIG["flask_port"])
        if port_pid:
            log(f"Found process using port {CONFIG['flask_port']}: PID {port_pid}")
            if stop_process(port_pid):
                log(f"Process {port_pid} terminated successfully", level="SUCCESS")
    
    # Find and stop any Flask/LogicLens processes
    pids = find_flask_processes()
    if pids:
        log(f"Found {len(pids)} LogicLens/Flask processes")
        for pid in pids:
            log(f"Stopping process {pid}...")
            if stop_process(pid):
                log(f"Process {pid} terminated successfully", level="SUCCESS")
    else:
        log("No LogicLens processes found running")
    
    # Final verification
    if is_port_in_use(CONFIG["flask_port"]):
        log(f"Port {CONFIG['flask_port']} is still in use after cleanup", level="WARNING")
        return False
    
    log("All LogicLens processes have been stopped", level="SUCCESS")
    return True


def create_log_entry(venv_python, log_type, message, details=None):
    """Create a log entry using the LogicLens logger."""
    backend_dir = Path(CONFIG["backend_dir"])
    
    if details is None:
        details = {}
    
    # Add standard details if not present
    if "timestamp" not in details:
        details["timestamp"] = datetime.datetime.now().isoformat()
    if "python_version" not in details:
        details["python_version"] = platform.python_version()
    if "os" not in details:
        details["os"] = f"{platform.system()} {platform.release()}"
    if "port" not in details:
        details["port"] = CONFIG["flask_port"]
    
    # Create a Python script to import and use the logger
    log_script = (
        "import sys; "
        "sys.path.append('.'); "
        "from app.utils.logger import get_logger; "
        "import json; "
        f"logger = get_logger('logiclens', {{'store_logs': True}}); "
        f"logger.log_event("
        f"    component='system', "
        f"    message='{message}', "
        f"    level='INFO', "
        f"    details={json.dumps(details)}"
        f");"
    )
    
    try:
        subprocess.run([str(venv_python), "-c", log_script], cwd=str(backend_dir), check=True)
        log(f"Created {log_type} log entry", level="SUCCESS")
        return True
    except subprocess.SubprocessError as e:
        log(f"Failed to create log entry: {e}", level="WARNING")
        return False


def generate_test_data(venv_python):
    """Generate test data for the application."""
    log("Generating test data...")
    backend_dir = Path(CONFIG["backend_dir"])
    
    # Create a Python script to generate test data
    test_data_script = """
import sys
sys.path.append('.')
from app.utils.test_utils import get_test_manager
from app.utils.monitoring import get_monitoring_manager
from app.utils.logger import get_logger
import random
import time
import datetime
import os
import platform

# Configure services
logger = get_logger('logiclens', {'store_logs': True})
test_manager = get_test_manager({'persist_results': True})
monitoring_manager = get_monitoring_manager({'persist_metrics': True})

# Log test data generation
logger.log_event(
    component='system',
    message='Starting test data generation via manage script',
    level='INFO',
    details={
        'timestamp': datetime.datetime.now().isoformat(),
        'python_version': platform.python_version(),
        'os': platform.system() + ' ' + platform.release()
    }
)

# Create test suites
test_suites = [
    'API Tests',
    'Frontend Tests',
    'Integration Tests',
    'Performance Tests'
]

suite_ids = {}

for suite_name in test_suites:
    suite_id = test_manager.start_suite(name=suite_name)
    suite_ids[suite_name] = suite_id
    logger.log_event(
        component='test',
        message=f'Created test suite: {suite_name}',
        level='INFO',
        details={'suite_id': suite_id}
    )
    
    # Add random test results
    for i in range(10):
        test_id = f'{suite_name.lower().replace(" ", "_")}_{i}'
        test_name = f'Test case {i} for {suite_name}'
        status = random.choice(['PASSED', 'PASSED', 'PASSED', 'FAILED', 'SKIPPED'])
        duration = random.uniform(0.1, 5.0)
        message = f'Test {"executed successfully" if status == "PASSED" else "failed with error X" if status == "FAILED" else "was skipped"}'
        
        test_result = test_manager.add_test_result(
            suite_id=suite_id,
            test_id=test_id,
            test_name=test_name,
            status=status,
            duration=duration,
            message=message
        )
        
        # Simulate test execution time
        time.sleep(0.05)
    
    # End the suite
    test_manager.end_suite(suite_id)

# Generate system metrics
for i in range(20):
    metrics = monitoring_manager.collect_metrics()
    
    # Add some random variation to simulate different loads
    variation = random.uniform(0.8, 1.2)
    if 'cpu' in metrics and 'percent' in metrics['cpu']:
        metrics['cpu']['percent'] = min(100, metrics['cpu']['percent'] * variation)
        
    if 'memory' in metrics and 'percent' in metrics['memory']:
        metrics['memory']['percent'] = min(100, metrics['memory']['percent'] * variation)
    
    # Add custom metrics
    metrics['custom'] = {
        'random_value': random.uniform(0, 100),
        'test_metric': random.randint(1, 1000),
        'api_latency': random.uniform(10, 500),
        'active_users': random.randint(1, 50),
        'requests_per_minute': random.randint(10, 200)
    }
    
    monitoring_manager.store_metrics(metrics)
    time.sleep(0.1)

# Log completion
logger.log_event(
    component='system',
    message='Test data generation completed successfully',
    level='INFO',
    details={
        'test_suites': len(test_suites),
        'metrics_generated': 20,
        'status': 'SUCCESS',
        'timestamp': datetime.datetime.now().isoformat()
    }
)

print('Test data generation complete!')
print(f'Created {len(test_suites)} test suites with 10 tests each')
print('Generated 20 system metric snapshots')
"""
    
    try:
        with open(backend_dir / "generate_test_data.py", "w") as f:
            f.write(test_data_script)
        
        subprocess.run([str(venv_python), "generate_test_data.py"], cwd=str(backend_dir), check=True)
        log("Test data generation completed successfully", level="SUCCESS")
        
        # Clean up the temporary script
        os.remove(backend_dir / "generate_test_data.py")
        return True
    except Exception as e:
        log(f"Failed to generate test data: {e}", level="ERROR")
        return False


def verify_ollama():
    """Verify Ollama is running and configured correctly."""
    if not CONFIG["ollama"]["enabled"]:
        log("Ollama integration is disabled in config", level="INFO")
        return True
    
    log("Verifying Ollama setup...", level="INFO")
    
    # Check if Ollama is installed
    ollama_cmd = "ollama" if platform.system() != "Windows" else "ollama.exe"
    if not shutil.which(ollama_cmd):
        if ERROR_HANDLER:
            error = LogicLensError("OLM_005", "Ollama is not installed or not in PATH")
            if ERROR_HANDLER.handle_error(error, context="Verifying Ollama"):
                return verify_ollama()  # Try again after recovery
        
        log("Ollama is not installed or not in PATH", level="WARNING")
        log("You can install it from: https://ollama.ai/download", level="INFO")
        log("LLM features will be disabled", level="WARNING")
        CONFIG["ollama"]["enabled"] = False
        return False
    
    # Check if Ollama service is running
    host = CONFIG["ollama"]["host"]
    try:
        with subprocess.Popen(
            ["curl", "-s", "-m", "3", f"{host}/api/tags"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            stdout, _ = process.communicate()
            
            if process.returncode != 0 or "error" in stdout.lower():
                if ERROR_HANDLER:
                    error = LogicLensError("OLM_001", "Ollama server is not running or unreachable")
                    if ERROR_HANDLER.handle_error(error, context="Checking Ollama server"):
                        return verify_ollama()  # Try again after recovery
                
                log(f"Ollama server is not running or unreachable at {host}", level="WARNING")
                log("LLM features will be disabled", level="WARNING")
                CONFIG["ollama"]["enabled"] = False
                return False
    except Exception:
        log(f"Failed to connect to Ollama at {host}", level="WARNING")
        log("LLM features will be disabled", level="WARNING")
        CONFIG["ollama"]["enabled"] = False
        return False
    
    # Check if model is available
    model = CONFIG["ollama"]["model"]
    try:
        with subprocess.Popen(
            ["curl", "-s", f"{host}/api/tags"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            stdout, _ = process.communicate()
            
            if process.returncode == 0 and model not in stdout:
                if ERROR_HANDLER:
                    error = LogicLensError("OLM_002", f"Ollama model '{model}' not found")
                    if ERROR_HANDLER.handle_error(error, context=f"Checking model {model}"):
                        return verify_ollama()  # Try again after recovery
                
                log(f"Ollama model '{model}' not found", level="WARNING")
                log(f"Available models: {stdout}", level="INFO")
                log("LLM features will be disabled", level="WARNING")
                CONFIG["ollama"]["enabled"] = False
                return False
    except Exception:
        log(f"Failed to check available models", level="WARNING")
        log("LLM features will be disabled", level="WARNING")
        CONFIG["ollama"]["enabled"] = False
        return False
    
    log(f"Ollama verified: using model '{model}' at {host}", level="SUCCESS")
    return True


def start_application():
    """Start the LogicLens application."""
    log("Starting LogicLens application...")
    
    # Ensure we're in the project root
    project_dir = Path.cwd()
    backend_dir = project_dir / CONFIG["backend_dir"]
    
    if not backend_dir.exists():
        if ERROR_HANDLER:
            error = LogicLensError("ENV_004", f"Backend directory '{CONFIG['backend_dir']}' not found")
            if ERROR_HANDLER.handle_error(error, context="Starting application"):
                # If recovery was successful, retry
                return start_application()
        
        log(f"Backend directory '{CONFIG['backend_dir']}' not found. Are you in the project root?", level="ERROR")
        sys.exit(1)
    
    # Log system diagnostics at startup
    if ERROR_HANDLER:
        ERROR_HANDLER._log_system_diagnostics()
    else:
        log_system_diagnostics()
    
    # First stop any running instances
    stop_application()
    
    # Check if port is available after cleanup
    if is_port_in_use(CONFIG["flask_port"]):
        if ERROR_HANDLER:
            error = LogicLensError("PRC_001", f"Port {CONFIG['flask_port']} is still in use")
            if ERROR_HANDLER.handle_error(error, context="Checking port availability"):
                # If recovery was successful (perhaps it changed the port), continue
                log(f"Using port {CONFIG['flask_port']} after recovery", level="INFO")
            else:
                log(f"Port {CONFIG['flask_port']} is still in use. Cannot start application.", level="ERROR")
                sys.exit(1)
        else:
            log(f"Port {CONFIG['flask_port']} is still in use. Cannot start application.", level="ERROR")
            sys.exit(1)
    
    # Set up environment
    venv_dir = create_or_update_venv()
    venv_python = get_venv_python(venv_dir)
    
    os.chdir(backend_dir)
    
    # Install dependencies
    if not install_dependencies(venv_dir):
        os.chdir(project_dir)
        sys.exit(1)
    
    # Set up .env file
    setup_env_file()
    
    # Verify Ollama if configured
    if CONFIG["ollama"]["verify_on_startup"]:
        verify_ollama()
    
    # Generate test data
    generate_test_data(venv_python)
    
    # Create startup log entry
    create_log_entry(
        venv_python,
        "startup",
        "Application started via management script",
        {
            "startup_mode": "management_script",
            "host": CONFIG["flask_host"],
            "port": CONFIG["flask_port"],
            "debug_mode": str(CONFIG["debug_mode"]).lower()
        }
    )
    
    # Set Flask environment variables
    env = os.environ.copy()
    env["FLASK_APP"] = "app"
    env["FLASK_ENV"] = "development" if CONFIG["debug_mode"] else "production"
    env["FLASK_DEBUG"] = "1" if CONFIG["debug_mode"] else "0"
    
    log(f"Starting Flask on {CONFIG['flask_host']}:{CONFIG['flask_port']} with debug={CONFIG['debug_mode']}")
    log(f"Press Ctrl+C to stop the server")
    
    # Start Flask
    try:
        flask_cmd = [
            str(venv_python), "-m", "flask", "run",
            "--host", CONFIG["flask_host"],
            "--port", str(CONFIG["flask_port"])
        ]
        
        flask_process = subprocess.Popen(flask_cmd, env=env)
        
        # Return to the project root
        os.chdir(project_dir)
        
        # Wait for Flask to start
        time.sleep(2)
        
        # Check if the process is still running
        if flask_process.poll() is None:
            log("LogicLens application started successfully", level="SUCCESS")
            
            # Keep running until interrupted
            try:
                flask_process.wait()
            except KeyboardInterrupt:
                log("Stopping LogicLens application...")
                flask_process.terminate()
                flask_process.wait(timeout=5)
                log("LogicLens application stopped", level="SUCCESS")
        else:
            if ERROR_HANDLER:
                error = LogicLensError("APP_001", f"Flask process terminated unexpectedly with exit code {flask_process.returncode}")
                if ERROR_HANDLER.handle_error(error, context="Starting Flask"):
                    # If recovery was successful, try again with potentially modified settings
                    os.chdir(project_dir)
                    return start_application()
            
            log("Flask process terminated unexpectedly with exit code " + str(flask_process.returncode), level="ERROR")
    except Exception as e:
        if ERROR_HANDLER:
            error = LogicLensError("APP_001", str(e), e)
            if ERROR_HANDLER.handle_error(error, context="Starting Flask application"):
                # If recovery was successful, try again
                os.chdir(project_dir)
                return start_application()
        
        log(f"Failed to start LogicLens application: {e}", level="ERROR")
        os.chdir(project_dir)
        sys.exit(1)


def check_status():
    """Check the status of the LogicLens application and environment."""
    log("Checking LogicLens status...")
    status = {
        "running": False,
        "port_in_use": False,
        "processes": [],
        "venv_exists": False,
        "python_version": None,
        "system": platform.system()
    }
    
    # Check if port is in use
    if is_port_in_use(CONFIG["flask_port"]):
        status["port_in_use"] = True
        port_pid = find_pid_by_port(CONFIG["flask_port"])
        if port_pid:
            status["processes"].append({"pid": port_pid, "type": "port"})
    
    # Find Flask/LogicLens processes
    pids = find_flask_processes()
    if pids:
        status["running"] = True
        for pid in pids:
            status["processes"].append({"pid": pid, "type": "process"})
    
    # Check virtual environment
    backend_dir = Path(CONFIG["backend_dir"])
    venv_dir = backend_dir / CONFIG["venv_dir"]
    if venv_dir.exists():
        status["venv_exists"] = True
        
        # Try to get Python version from venv
        venv_python = get_venv_python(venv_dir)
        try:
            output = subprocess.check_output([str(venv_python), "--version"], text=True)
            status["python_version"] = output.strip()
        except subprocess.SubprocessError:
            pass
    
    # Print status
    log("===== LogicLens Status =====")
    log(f"System: {status['system']}")
    log(f"Running: {'Yes' if status['running'] else 'No'}")
    if status["port_in_use"]:
        log(f"Port {CONFIG['flask_port']} is in use")
    if status["processes"]:
        log(f"Found {len(status['processes'])} LogicLens processes")
        for proc in status["processes"]:
            log(f"  PID: {proc['pid']} ({proc['type']})")
    log(f"Virtual environment: {'Exists' if status['venv_exists'] else 'Not found'}")
    if status["python_version"]:
        log(f"Python version: {status['python_version']}")
    log("===========================")
    
    return status


def setup_environment():
    """Set up the environment without starting the application."""
    log("Setting up LogicLens environment...")
    
    # Ensure we're in the project root
    project_dir = Path.cwd()
    backend_dir = project_dir / CONFIG["backend_dir"]
    
    if not backend_dir.exists():
        log(f"Backend directory '{CONFIG['backend_dir']}' not found. Are you in the project root?", level="ERROR")
        sys.exit(1)
    
    # Set up environment
    venv_dir = create_or_update_venv()
    venv_python = get_venv_python(venv_dir)
    
    os.chdir(backend_dir)
    
    # Install dependencies
    if not install_dependencies(venv_dir):
        os.chdir(project_dir)
        sys.exit(1)
    
    # Set up .env file
    setup_env_file()
    
    # Generate test data
    generate_test_data(venv_python)
    
    os.chdir(project_dir)
    log("LogicLens environment setup completed successfully", level="SUCCESS")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="LogicLens Application Manager")
    parser.add_argument("command", choices=["start", "stop", "setup", "test", "status", "ollama"], 
                      help="Command to run")
    parser.add_argument("--port", type=int, default=CONFIG["flask_port"],
                      help=f"Port for Flask to listen on (default: {CONFIG['flask_port']})")
    parser.add_argument("--host", default=CONFIG["flask_host"],
                      help=f"Host for Flask to bind to (default: {CONFIG['flask_host']})")
    parser.add_argument("--no-debug", action="store_true",
                      help="Disable debug mode")
    
    # Ollama specific arguments
    parser.add_argument("--ollama-host", 
                      help="Ollama host URL (e.g., http://localhost:11434)")
    parser.add_argument("--ollama-model", 
                      help="Ollama model to use")
    parser.add_argument("--list-models", action="store_true",
                      help="List available Ollama models")
    parser.add_argument("--verify", action="store_true",
                      help="Verify Ollama setup")
    
    args = parser.parse_args()
    
    # Update config from arguments
    CONFIG["flask_port"] = args.port
    CONFIG["flask_host"] = args.host
    CONFIG["debug_mode"] = not args.no_debug
    
    if args.ollama_host:
        CONFIG["ollama"]["host"] = args.ollama_host
    
    if args.ollama_model:
        CONFIG["ollama"]["model"] = args.ollama_model
    
    try:
        if args.command == "start":
            start_application()
        elif args.command == "stop":
            stop_application()
        elif args.command == "setup":
            setup_environment()
        elif args.command == "test":
            # Ensure we're in the project root
            project_dir = Path.cwd()
            backend_dir = project_dir / CONFIG["backend_dir"]
            
            if not backend_dir.exists():
                log(f"Backend directory '{CONFIG['backend_dir']}' not found. Are you in the project root?", level="ERROR")
                sys.exit(1)
                
            venv_dir = create_or_update_venv()
            venv_python = get_venv_python(venv_dir)
            
            os.chdir(backend_dir)
            generate_test_data(venv_python)
            os.chdir(project_dir)
        elif args.command == "status":
            check_status()
        elif args.command == "ollama":
            # Handle Ollama related commands
            configure_ollama(args)
    except KeyboardInterrupt:
        log("Operation interrupted by user", level="WARNING")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        if ERROR_HANDLER:
            # Try to identify and handle the error
            log("An error occurred. Attempting recovery...", level="ERROR")
            
            # Get traceback for context
            tb = traceback.format_exc()
            
            # Create a generic error if we can't map it to a specific one
            error = ERROR_HANDLER._map_exception_to_error(e, context=f"Command: {args.command}")
            
            # Log the full traceback
            log(f"Error details: {tb}", level="ERROR")
            
            # Try to recover
            if ERROR_HANDLER.handle_error(error, context=f"Command: {args.command}"):
                log("Recovery was successful. Please try your command again.", level="SUCCESS")
                sys.exit(0)
            else:
                log("Recovery was not successful. Please check the logs and try again.", level="ERROR")
        else:
            log(f"An unhandled error occurred: {e}", level="ERROR")
            traceback.print_exc()
        
        sys.exit(1)


def configure_ollama(args):
    """Configure and manage Ollama integration."""
    log("Ollama Configuration", level="INFO")
    
    if args.list_models:
        log("Checking available Ollama models...", level="INFO")
        try:
            # Try to import setup_env_file module with get_available_models function
            try:
                from setup_env_file import get_available_models
                models = get_available_models()
            except ImportError:
                # Fallback to direct command
                ollama_cmd = "ollama" if platform.system() != "Windows" else "ollama.exe"
                if not shutil.which(ollama_cmd):
                    log("Ollama is not installed or not in PATH", level="ERROR")
                    log("You can install it from: https://ollama.ai/download", level="INFO")
                    return
                    
                result = subprocess.run([ollama_cmd, "list"], capture_output=True, text=True)
                if result.returncode != 0:
                    log(f"Error listing models: {result.stderr}", level="ERROR")
                    return
                
                # Parse output
                output = result.stdout.strip()
                models = []
                for line in output.split("\n")[1:]:  # Skip header line
                    if line.strip():
                        parts = line.split()
                        if parts:
                            models.append(parts[0])
            
            if models:
                log("Available models:", level="INFO")
                for model in models:
                    log(f"  - {model}", level="INFO")
            else:
                log("No models available or Ollama not running", level="WARNING")
        except Exception as e:
            log(f"Error listing models: {e}", level="ERROR")
            return
    
    if args.verify:
        verify_ollama()
        return
    
    # Update Ollama config in .env file
    if args.ollama_host or args.ollama_model:
        log("Updating Ollama configuration...", level="INFO")
        try:
            # Try to import setup_env_file module with update_ollama_config function
            try:
                from setup_env_file import update_ollama_config
                update_ollama_config(CONFIG["backend_dir"], args.ollama_model, args.ollama_host)
            except ImportError:
                # Fallback to manual update
                backend_dir = Path(CONFIG["backend_dir"])
                env_file = backend_dir / ".env"
                env_example = backend_dir / ".env.example"
                
                # Create .env from .env.example if it doesn't exist
                if not env_file.exists():
                    if env_example.exists():
                        log("Creating .env file from example...", level="INFO")
                        shutil.copy(env_example, env_file)
                    else:
                        log(".env.example file not found", level="ERROR")
                        return
                
                # Read current .env file
                with open(env_file, "r") as f:
                    lines = f.readlines()
                
                # Update the configuration
                ollama_host_found = False
                ollama_model_found = False
                new_lines = []
                
                for line in lines:
                    if line.strip().startswith("OLLAMA_HOST="):
                        ollama_host_found = True
                        if args.ollama_host:
                            new_lines.append(f"OLLAMA_HOST={args.ollama_host}\n")
                        else:
                            new_lines.append(line)
                    elif line.strip().startswith("OLLAMA_MODEL="):
                        ollama_model_found = True
                        if args.ollama_model:
                            new_lines.append(f"OLLAMA_MODEL={args.ollama_model}\n")
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)
                
                # Add settings if not found
                if not ollama_host_found and args.ollama_host:
                    new_lines.append(f"OLLAMA_HOST={args.ollama_host}\n")
                
                if not ollama_model_found and args.ollama_model:
                    new_lines.append(f"OLLAMA_MODEL={args.ollama_model}\n")
                
                # Write updated content
                with open(env_file, "w") as f:
                    f.writelines(new_lines)
            
            log("Ollama configuration updated", level="SUCCESS")
            
            # Update current config
            if args.ollama_host:
                CONFIG["ollama"]["host"] = args.ollama_host
            if args.ollama_model:
                CONFIG["ollama"]["model"] = args.ollama_model
            
            # Verify configuration
            verify_ollama()
            
        except Exception as e:
            log(f"Error updating Ollama configuration: {e}", level="ERROR")
            return
    
    # If no args provided, just show current config
    if not (args.list_models or args.verify or args.ollama_host or args.ollama_model):
        log("Current Ollama configuration:", level="INFO")
        log(f"  Host: {CONFIG['ollama']['host']}", level="INFO")
        log(f"  Model: {CONFIG['ollama']['model']}", level="INFO")
        log(f"  Enabled: {CONFIG['ollama']['enabled']}", level="INFO")
        log("Use --help for available options", level="INFO")


if __name__ == "__main__":
    main() 