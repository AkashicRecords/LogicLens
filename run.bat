@echo off
setlocal enabledelayedexpansion

:: Script configuration
set VENV_DIR=venv
set PYTHON_VERSION=python3.8
set REQUIREMENTS_FILE=requirements.txt
set FLASK_APP=app
set BACKEND_DIR=backend
set FLASK_PORT=5050

:: Check if we're in the project root
if not exist "%BACKEND_DIR%" (
    echo Error: Please run this script from the project root directory
    exit /b 1
)

:: Change to backend directory
cd "%BACKEND_DIR%"
echo [LOGICLENS] Changed to backend directory

:: Check if Python is installed
where %PYTHON_VERSION% >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: %PYTHON_VERSION% could not be found.
    echo Please install Python 3.8 or higher.
    exit /b 1
)

:: Check if virtual environment exists, create if not
if not exist "%VENV_DIR%" (
    echo [LOGICLENS] Creating virtual environment with %PYTHON_VERSION%...
    %PYTHON_VERSION% -m venv "%VENV_DIR%"
)

:: Activate virtual environment
echo [LOGICLENS] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

:: Verify Python version in virtual environment
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION_FULL=%%i
echo [LOGICLENS] Using !PYTHON_VERSION_FULL!

:: Install or update dependencies
if exist "%REQUIREMENTS_FILE%" (
    echo [LOGICLENS] Installing requirements...
    pip install -r "%REQUIREMENTS_FILE%"
) else (
    echo [LOGICLENS] Installing package in development mode...
    pip install -e ..
)

:: Check for .env file and create from example if missing
if not exist ".env" (
    if exist ".env.example" (
        echo [LOGICLENS] Creating .env file from example...
        copy ".env.example" ".env"
        echo Warning: .env file created from example. You may want to update it with your configuration.
    )
)

:: Set Flask environment variables if not already set
if not defined FLASK_APP set FLASK_APP=app
if not defined FLASK_ENV set FLASK_ENV=development
if not defined FLASK_DEBUG set FLASK_DEBUG=1

:: Create a startup log entry
echo [LOGICLENS] Creating startup log entry...
python -c "import sys; try: sys.path.append('.'); from app.utils.logger import get_logger; import platform, datetime, os; logger = get_logger('logiclens', {'store_logs': True}); logger.log_event(component='system', message='Application started via startup script (Windows)', level='INFO', details={'timestamp': datetime.datetime.now().isoformat(), 'python_version': platform.python_version(), 'os': platform.system(), 'environment': os.environ.get('FLASK_ENV', 'development'), 'debug_mode': os.environ.get('FLASK_DEBUG', 'false'), 'host': '0.0.0.0', 'port': %FLASK_PORT%}); print('Startup log entry created successfully'); except Exception as e: print(f'Error creating startup log: {e}');"

echo [LOGICLENS] Starting Flask application...
echo [LOGICLENS] Environment: %FLASK_ENV%
echo [LOGICLENS] Debug mode: %FLASK_DEBUG%
echo [LOGICLENS] Port: %FLASK_PORT%
echo [LOGICLENS] Press CTRL+C to stop the server

:: Run Flask on port 5050
flask run --host=0.0.0.0 --port=%FLASK_PORT%

:: This will not be reached unless flask exits normally
echo [LOGICLENS] Flask server has stopped.
endlocal 