#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Script configuration
VENV_DIR="venv"
PYTHON_VERSION="python3.8"  # Using Python 3.8 which is compatible with the application
REQUIREMENTS_FILE="requirements.txt"
FLASK_APP="app"
BACKEND_DIR="backend"
FLASK_PORT=5050  # Changed from 5000 to avoid conflict with Control Center

# Print with colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function to print status messages
print_status() {
    echo -e "${GREEN}[LOGICLENS]${NC} $1"
}

# Check if we're in the project root
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Change to backend directory
cd "$BACKEND_DIR"
print_status "Changed to backend directory"

# Check if Python is installed
if ! command -v $PYTHON_VERSION &> /dev/null; then
    echo -e "${RED}Error: $PYTHON_VERSION could not be found.${NC}"
    echo -e "${YELLOW}Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_DIR" ]; then
    print_status "Creating virtual environment with $PYTHON_VERSION..."
    $PYTHON_VERSION -m venv "$VENV_DIR"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify Python version in virtual environment
PYTHON_VERSION_FULL=$(python --version)
print_status "Using $PYTHON_VERSION_FULL"

# Install or update dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    print_status "Installing requirements..."
    pip install -r "$REQUIREMENTS_FILE"
else
    print_status "Installing package in development mode..."
    pip install -e ..
fi

# Check for .env file and create from example if missing
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    print_status "Creating .env file from example..."
    cp .env.example .env
    echo -e "${YELLOW}Warning: .env file created from example. You may want to update it with your configuration.${NC}"
fi

# Set Flask environment variables if not already set
export FLASK_APP="${FLASK_APP:-app}"
export FLASK_ENV="${FLASK_ENV:-development}"
export FLASK_DEBUG="${FLASK_DEBUG:-1}"

# Create a startup log entry
print_status "Creating startup log entry..."
python -c "
import sys
try:
    sys.path.append('.')
    from app.utils.logger import get_logger
    import platform, datetime, os

    logger = get_logger('logiclens', {'store_logs': True})
    logger.log_event(
        component='system',
        message='Application started via startup script',
        level='INFO',
        details={
            'timestamp': datetime.datetime.now().isoformat(),
            'python_version': platform.python_version(),
            'os': platform.system(),
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'debug_mode': os.environ.get('FLASK_DEBUG', 'false'),
            'host': '0.0.0.0',
            'port': $FLASK_PORT
        }
    )
    print('Startup log entry created successfully')
except Exception as e:
    print(f'Error creating startup log: {e}')
"

print_status "Starting Flask application..."
print_status "Environment: $FLASK_ENV"
print_status "Debug mode: $FLASK_DEBUG"
print_status "Port: $FLASK_PORT"
print_status "Press CTRL+C to stop the server"

# Run Flask on port 5050
flask run --host=0.0.0.0 --port=$FLASK_PORT

# This will not be reached unless flask exits normally
print_status "Flask server has stopped." 