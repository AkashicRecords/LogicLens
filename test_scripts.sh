#!/bin/bash

# Exit on error
set -e

# Print with colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function to print status messages
print_status() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

# Change to project root if needed
if [ -d "backend" ]; then
    ROOT_DIR=$(pwd)
    BACKEND_DIR="$ROOT_DIR/backend"
else
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Function to test if run.sh and shutdown.sh exist and are executable
test_script_existence() {
    print_status "Testing script existence..."
    
    if [ ! -f "run.sh" ]; then
        echo -e "${RED}Error: run.sh does not exist in the current directory${NC}"
        exit 1
    fi
    
    if [ ! -f "shutdown.sh" ]; then
        echo -e "${RED}Error: shutdown.sh does not exist in the current directory${NC}"
        exit 1
    fi
    
    # Make scripts executable if they aren't already
    chmod +x run.sh
    chmod +x shutdown.sh
    chmod +x test_scripts.sh
    
    print_status "All scripts exist and are executable ✓"
}

# Set up environment for testing
setup_test_env() {
    print_status "Setting up test environment..."
    
    # Create test directory if it doesn't exist
    mkdir -p "$BACKEND_DIR/test_results"
    
    print_status "Test environment set up ✓"
}

# Generate test data
generate_test_data() {
    print_status "Generating test data..."
    
    # Activate virtual environment
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        print_status "Creating virtual environment first..."
        python3.8 -m venv venv
        source venv/bin/activate
        pip install -e ..
    fi
    
    # Generate test suite data
    python -c "
import sys
try:
    sys.path.append('.')
    from app.utils.test_utils import get_test_manager
    from app.utils.monitoring import get_monitoring_manager
    from app.utils.logger import get_logger
    import random
    import time
    import datetime
    
    # Configure services
    logger = get_logger('logiclens', {'store_logs': True})
    test_manager = get_test_manager({'persist_results': True})
    monitoring_manager = get_monitoring_manager({'persist_metrics': True})
    
    # Log test execution
    logger.log_event(
        component='test',
        message='Starting test script execution',
        level='INFO',
        details={'timestamp': datetime.datetime.now().isoformat()}
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
            time.sleep(0.1)
        
        # End the suite
        test_manager.end_suite(suite_id)
    
    # Generate system metrics
    for i in range(20):
        metrics = monitoring_manager.collect_metrics()
        metrics['custom'] = {
            'random_value': random.uniform(0, 100),
            'test_metric': random.randint(1, 1000)
        }
        monitoring_manager.store_metrics(metrics)
        time.sleep(0.2)
    
    # Log completion
    logger.log_event(
        component='test',
        message='Test script execution completed',
        level='INFO',
        details={
            'timestamp': datetime.datetime.now().isoformat(),
            'test_suites_created': len(test_suites),
            'metrics_generated': 20
        }
    )
    
    print('Test data generation complete!')
    print(f'Created {len(test_suites)} test suites with 10 tests each')
    print('Generated 20 system metric snapshots')
    
except Exception as e:
    print(f'Error generating test data: {e}')
"
    
    # Deactivate virtual environment
    deactivate
    
    cd "$ROOT_DIR"
    print_status "Test data generated ✓"
}

# Test startup script
test_startup_script() {
    print_status "Testing startup script..."
    
    # Run the startup script in background with timeout
    print_status "Starting application with timeout of 10 seconds..."
    
    # Use timeout to run for only 10 seconds
    timeout 10s ./run.sh &
    APP_PID=$!
    
    # Wait a bit for the app to start
    sleep 5
    
    # Check if the process is still running
    if ps -p $APP_PID > /dev/null; then
        print_status "Application started successfully ✓"
    else
        echo -e "${RED}Error: Application failed to start${NC}"
        exit 1
    fi
    
    # Allow the timeout to complete
    wait $APP_PID || true
    
    print_status "Startup script test completed ✓"
}

# Test shutdown script
test_shutdown_script() {
    print_status "Testing shutdown script..."
    
    # Start the application in background
    print_status "Starting application..."
    ./run.sh &
    APP_PID=$!
    
    # Wait a bit for the app to start
    sleep 5
    
    # Check if the process is running
    if ps -p $APP_PID > /dev/null; then
        print_status "Application started successfully ✓"
        
        # Run the shutdown script
        print_status "Running shutdown script..."
        ./shutdown.sh
        
        # Wait a moment
        sleep 2
        
        # Check if the process is still running
        if ps -p $APP_PID > /dev/null; then
            echo -e "${RED}Error: Application is still running after shutdown script${NC}"
            # Forcefully kill the process
            kill -9 $APP_PID
            exit 1
        else
            print_status "Application was shut down successfully ✓"
        fi
    else
        echo -e "${RED}Error: Application failed to start for shutdown test${NC}"
        exit 1
    fi
    
    print_status "Shutdown script test completed ✓"
}

# Run all tests
run_all_tests() {
    print_status "Starting script tests..."
    
    test_script_existence
    setup_test_env
    generate_test_data
    test_startup_script
    test_shutdown_script
    
    print_status "All tests completed successfully! ✓"
}

# Execute all tests
run_all_tests 