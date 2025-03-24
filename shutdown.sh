#!/bin/bash

# Print with colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Port configuration
FLASK_PORT=5050  # Updated from 5000 to 5050

# Helper function to print status messages
print_status() {
    echo -e "${GREEN}[LOGICLENS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[LOGICLENS]${NC} $1"
}

print_error() {
    echo -e "${RED}[LOGICLENS]${NC} $1"
}

# Function to find the Flask process
find_flask_process() {
    # Look for Flask processes
    ps aux | grep -E "flask run|python.*app\.py|gunicorn|logiclens web" | grep -v grep | awk '{print $2}'
}

verify_port_available() {
    local port="$1"
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i :"$port" > /dev/null 2>&1; then
            print_warning "Port $port is still in use!"
            return 1
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -an | grep "LISTEN" | grep -q ":$port "; then
            print_warning "Port $port is still in use!"
            return 1
        fi
    else
        print_warning "Cannot verify port availability (lsof/netstat not available)"
    fi
    return 0
}

# Check if we're in the project root
if [ -d "backend" ]; then
    cd backend
    print_status "Changed to backend directory"
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
fi

# Create a shutdown log entry
print_status "Creating shutdown log entry..."
python -c "
import sys
try:
    sys.path.append('.')
    from app.utils.logger import get_logger
    import platform, datetime, os

    logger = get_logger('logiclens', {'store_logs': True})
    logger.log_event(
        component='system',
        message='Application shutdown via shutdown script',
        level='INFO',
        details={
            'timestamp': datetime.datetime.now().isoformat(),
            'python_version': platform.python_version(),
            'os': platform.system(),
            'shutdown_type': 'manual',
            'verification': 'strict',
            'port': $FLASK_PORT
        }
    )
    print('Shutdown log entry created successfully')
except Exception as e:
    print(f'Error creating shutdown log: {e}')
"

# Find all running Flask processes
print_status "Finding all running LogicLens processes..."
FLASK_PIDS=$(find_flask_process)

if [ -z "$FLASK_PIDS" ]; then
    print_status "No LogicLens application processes found running."
else
    # Count the processes
    NUM_PROCESSES=$(echo "$FLASK_PIDS" | wc -l)
    print_status "Found $NUM_PROCESSES LogicLens processes running."

    # Terminate each found process
    for PID in $FLASK_PIDS; do
        print_status "Shutting down LogicLens application (PID: $PID)"
        
        # First try a graceful shutdown with SIGTERM
        kill -15 $PID 2>/dev/null
        
        # Wait for the process to terminate gracefully
        for i in {1..5}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                print_status "Process $PID successfully terminated."
                break
            fi
            print_status "Waiting for process to terminate... ($i/5)"
            sleep 1
        done
        
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            print_warning "Process $PID did not terminate gracefully. Forcing termination..."
            kill -9 $PID 2>/dev/null
            sleep 1
            if ! ps -p $PID > /dev/null 2>&1; then
                print_status "Process $PID forcefully terminated."
            else
                print_error "Failed to terminate process $PID. Please terminate it manually."
            fi
        fi
    done
fi

# Check for any remaining Python processes that might be related
PYTHON_PIDS=$(ps aux | grep -E "python.*flask|python.*app\.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PYTHON_PIDS" ]; then
    print_warning "Found additional Python processes that might be related to LogicLens:"
    ps aux | grep -E "python.*flask|python.*app\.py" | grep -v grep
    
    for PID in $PYTHON_PIDS; do
        print_warning "Terminating potential LogicLens process (PID: $PID)"
        kill -9 $PID 2>/dev/null
    done
fi

# Verify that port is free
print_status "Verifying port availability..."
if ! verify_port_available $FLASK_PORT; then
    print_error "Port $FLASK_PORT is still in use after cleanup! This might cause problems when starting the application."
    print_status "Attempting to force release port $FLASK_PORT..."
    
    if command -v lsof >/dev/null 2>&1; then
        PORT_PID=$(lsof -i :$FLASK_PORT -t 2>/dev/null)
        if [ ! -z "$PORT_PID" ]; then
            print_warning "Killing process using port $FLASK_PORT (PID: $PORT_PID)"
            kill -9 $PORT_PID 2>/dev/null
            sleep 1
            if verify_port_available $FLASK_PORT; then
                print_status "Successfully released port $FLASK_PORT"
            else
                print_error "Failed to release port $FLASK_PORT. Please restart your system if this persists."
            fi
        fi
    fi
else
    print_status "Port $FLASK_PORT is available ✓"
fi

# Check for stale PID files or lock files
print_status "Cleaning up stale files..."
if [ -f ".flask.pid" ]; then
    rm -f .flask.pid
    print_status "Removed stale .flask.pid file"
fi

if [ -f ".gunicorn.pid" ]; then
    rm -f .gunicorn.pid
    print_status "Removed stale .gunicorn.pid file"
fi

print_status "Shutdown complete. Environment is clean."

# Optionally deactivate the virtual environment if it's active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_status "Deactivating virtual environment..."
    deactivate 2>/dev/null || true
fi 