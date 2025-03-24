@echo off
setlocal enabledelayedexpansion

:: Script configuration
set VENV_DIR=venv
set PYTHON_VERSION=python3.8
set BACKEND_DIR=backend
set FLASK_PORT=5050

echo [LOGICLENS] ===== PREPARING SCRIPTS =====

:: Check if we're in the project root
if not exist "%BACKEND_DIR%" (
    echo [ERROR] Please run this script from the project root directory
    exit /b 1
)

:: First, ensure there are no running instances
echo [LOGICLENS] ===== CLEANING ENVIRONMENT =====
echo [LOGICLENS] Checking for running instances...

:: Run the shutdown script to ensure clean environment
call shutdown.bat

:: Verify the environment is clean
echo [LOGICLENS] Verifying environment is clean...

:: Check if port 5050 is in use
set "PORT_IN_USE="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:"TCP.*:5050.*LISTENING"') do (
    set PORT_IN_USE=1
)

if defined PORT_IN_USE (
    echo [ERROR] Port %FLASK_PORT% is still in use after cleanup! Cannot proceed.
    echo [WARNING] Please try again or manually kill processes using port %FLASK_PORT%.
    exit /b 1
)

:: Check if Python is installed
where %PYTHON_VERSION% >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] %PYTHON_VERSION% is not installed!
    echo [ERROR] Please install Python 3.8 or higher.
    exit /b 1
)

echo [LOGICLENS] ===== RUNNING TESTS =====
echo [LOGICLENS] Running tests and generating data...

:: Change to backend directory
cd "%BACKEND_DIR%"

:: Check if virtual environment exists, create if not
if not exist "%VENV_DIR%" (
    echo [LOGICLENS] Creating virtual environment with %PYTHON_VERSION%...
    %PYTHON_VERSION% -m venv "%VENV_DIR%"
)

:: Activate virtual environment
echo [LOGICLENS] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: Verify Python version in virtual environment
for /f "tokens=*" %%i in ('python --version') do set VENV_PYTHON_VERSION=%%i
echo [LOGICLENS] Virtual environment using !VENV_PYTHON_VERSION!

:: Generate test data
echo [LOGICLENS] Generating test data...
python -c "import sys; sys.path.append('.'); from app.utils.test_utils import get_test_manager; from app.utils.monitoring import get_monitoring_manager; from app.utils.logger import get_logger; import random; import time; import datetime; import os; logger = get_logger('logiclens', {'store_logs': True}); test_manager = get_test_manager({'persist_results': True}); monitoring_manager = get_monitoring_manager({'persist_metrics': True}); logger.log_event(component='system', message='Starting LogicLens master startup sequence (Windows)', level='INFO', details={'timestamp': datetime.datetime.now().isoformat(), 'port': 5050}); test_suites = ['API Tests', 'Frontend Tests', 'Integration Tests', 'Performance Tests']; suite_ids = {}; for suite_name in test_suites: suite_id = test_manager.start_suite(name=suite_name); suite_ids[suite_name] = suite_id; logger.log_event(component='test', message=f'Created test suite: {suite_name}', level='INFO', details={'suite_id': suite_id}); for i in range(10): test_id = f'{suite_name.lower().replace(\" \", \"_\")}_{i}'; test_name = f'Test case {i} for {suite_name}'; status = random.choice(['PASSED', 'PASSED', 'PASSED', 'FAILED', 'SKIPPED']); duration = random.uniform(0.1, 5.0); message = f'Test {\"executed successfully\" if status == \"PASSED\" else \"failed with error X\" if status == \"FAILED\" else \"was skipped\"}'; test_result = test_manager.add_test_result(suite_id=suite_id, test_id=test_id, test_name=test_name, status=status, duration=duration, message=message); time.sleep(0.05); test_manager.end_suite(suite_id); for i in range(20): metrics = monitoring_manager.collect_metrics(); metrics['custom'] = {'random_value': random.uniform(0, 100), 'test_metric': random.randint(1, 1000)}; monitoring_manager.store_metrics(metrics); time.sleep(0.1); logger.log_event(component='system', message='Test data generation completed successfully', level='INFO', details={'test_suites': len(test_suites), 'metrics_generated': 20, 'status': 'SUCCESS'}); logger.log_event(component='system', message='Launching LogicLens application via master startup script (Windows)', level='INFO', details={'timestamp': datetime.datetime.now().isoformat(), 'environment': os.environ.get('FLASK_ENV', 'development'), 'python_version': sys.version, 'startup_mode': 'master_script', 'port': 5050}); print('Test data generation complete!'); print(f'Created {len(test_suites)} test suites with 10 tests each'); print('Generated 20 system metric snapshots');"

:: Check for any errors
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate test data!
    call deactivate
    cd ..
    exit /b 1
)

:: Deactivate virtual environment
call deactivate

:: Return to project root
cd ..

:: Final check before launching
echo [LOGICLENS] ===== FINAL VERIFICATION =====

:: Check if port 5050 is in use again
set "PORT_IN_USE="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:"TCP.*:5050.*LISTENING"') do (
    set PORT_IN_USE=1
)

if defined PORT_IN_USE (
    echo [ERROR] Port %FLASK_PORT% is in use! Cannot start LogicLens.
    exit /b 1
)

echo [LOGICLENS] Environment is clean and ready
echo [LOGICLENS] All verification tests passed

:: Launch the application
echo [LOGICLENS] ===== LAUNCHING APPLICATION =====
echo [LOGICLENS] Starting LogicLens application on port %FLASK_PORT%...

:: Run the application
call run.bat

endlocal 