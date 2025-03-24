@echo off
setlocal enabledelayedexpansion

echo [TEST] Starting script tests...

:: Check if we're in the project root
if not exist "backend" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

set ROOT_DIR=%cd%
set BACKEND_DIR=%ROOT_DIR%\backend

:: Test script existence
echo [TEST] Testing script existence...

if not exist "run.bat" (
    echo Error: run.bat does not exist in the current directory
    exit /b 1
)

if not exist "shutdown.bat" (
    echo Error: shutdown.bat does not exist in the current directory
    exit /b 1
)

echo [TEST] All scripts exist ✓

:: Set up environment for testing
echo [TEST] Setting up test environment...

:: Create test directory if it doesn't exist
if not exist "%BACKEND_DIR%\test_results" (
    mkdir "%BACKEND_DIR%\test_results"
)

echo [TEST] Test environment set up ✓

:: Generate test data
echo [TEST] Generating test data...

:: Change to backend directory
cd "%BACKEND_DIR%"

:: Activate virtual environment
if exist "venv" (
    call venv\Scripts\activate.bat
) else (
    echo [TEST] Creating virtual environment first...
    python3.8 -m venv venv
    call venv\Scripts\activate.bat
    pip install -e ..
)

:: Generate test suite data
python -c "import sys; sys.path.append('.'); from app.utils.test_utils import get_test_manager; from app.utils.monitoring import get_monitoring_manager; from app.utils.logger import get_logger; import random; import time; import datetime; logger = get_logger('logiclens', {'store_logs': True}); test_manager = get_test_manager({'persist_results': True}); monitoring_manager = get_monitoring_manager({'persist_metrics': True}); logger.log_event(component='test', message='Starting test script execution (Windows)', level='INFO', details={'timestamp': datetime.datetime.now().isoformat()}); test_suites = ['API Tests', 'Frontend Tests', 'Integration Tests', 'Performance Tests']; suite_ids = {}; for suite_name in test_suites: suite_id = test_manager.start_suite(name=suite_name); suite_ids[suite_name] = suite_id; logger.log_event(component='test', message=f'Created test suite: {suite_name}', level='INFO', details={'suite_id': suite_id}); for i in range(10): test_id = f'{suite_name.lower().replace(\" \", \"_\")}_{i}'; test_name = f'Test case {i} for {suite_name}'; status = random.choice(['PASSED', 'PASSED', 'PASSED', 'FAILED', 'SKIPPED']); duration = random.uniform(0.1, 5.0); message = f'Test {\"executed successfully\" if status == \"PASSED\" else \"failed with error X\" if status == \"FAILED\" else \"was skipped\"}'; test_result = test_manager.add_test_result(suite_id=suite_id, test_id=test_id, test_name=test_name, status=status, duration=duration, message=message); time.sleep(0.1); test_manager.end_suite(suite_id); for i in range(20): metrics = monitoring_manager.collect_metrics(); metrics['custom'] = {'random_value': random.uniform(0, 100), 'test_metric': random.randint(1, 1000)}; monitoring_manager.store_metrics(metrics); time.sleep(0.2); logger.log_event(component='test', message='Test script execution completed', level='INFO', details={'timestamp': datetime.datetime.now().isoformat(), 'test_suites_created': len(test_suites), 'metrics_generated': 20}); print('Test data generation complete!'); print(f'Created {len(test_suites)} test suites with 10 tests each'); print('Generated 20 system metric snapshots');"

:: Deactivate virtual environment
call deactivate

:: Change back to root directory
cd "%ROOT_DIR%"

echo [TEST] Test data generated ✓

:: Test startup script
echo [TEST] Testing startup script...

:: Start the app in a separate window with a timeout
echo [TEST] Starting application for testing (will auto-close)...
start /b cmd /c "run.bat & timeout /t 10 & taskkill /f /im python.exe /fi "WINDOWTITLE eq LogicLens*""

:: Wait a moment
timeout /t 5 /nobreak > NUL

:: Check if process is running (using a different approach since PID tracking is harder in batch)
set "FOUND_PROCESS="
for /f "tokens=1" %%p in ('tasklist /fi "IMAGENAME eq python.exe" /fo csv /nh ^| findstr /i "flask"') do (
    set FOUND_PROCESS=1
)

if defined FOUND_PROCESS (
    echo [TEST] Application started successfully ✓
) else (
    echo [TEST] Error: Application failed to start
    exit /b 1
)

:: Wait for auto-shutdown from the timeout above
timeout /t 6 /nobreak > NUL

echo [TEST] Startup script test completed ✓

:: Test shutdown script
echo [TEST] Testing shutdown script...

:: Start the application
echo [TEST] Starting application...
start /b cmd /c "run.bat"

:: Wait a bit for the app to start
timeout /t 5 /nobreak > NUL

:: Check if process is running
set "FOUND_PROCESS="
for /f "tokens=1" %%p in ('tasklist /fi "IMAGENAME eq python.exe" /fo csv /nh ^| findstr /i "flask"') do (
    set FOUND_PROCESS=1
)

if defined FOUND_PROCESS (
    echo [TEST] Application started successfully ✓
    
    :: Run the shutdown script
    echo [TEST] Running shutdown script...
    call shutdown.bat
    
    :: Wait a moment
    timeout /t 2 /nobreak > NUL
    
    :: Check if process is still running
    set "STILL_RUNNING="
    for /f "tokens=1" %%p in ('tasklist /fi "IMAGENAME eq python.exe" /fo csv /nh ^| findstr /i "flask"') do (
        set STILL_RUNNING=1
    )
    
    if defined STILL_RUNNING (
        echo [TEST] Error: Application is still running after shutdown script
        taskkill /f /im python.exe /fi "WINDOWTITLE eq LogicLens*"
        exit /b 1
    ) else (
        echo [TEST] Application was shut down successfully ✓
    )
) else (
    echo [TEST] Error: Application failed to start for shutdown test
    exit /b 1
)

echo [TEST] Shutdown script test completed ✓
echo [TEST] All tests completed successfully! ✓

endlocal 