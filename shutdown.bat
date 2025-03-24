@echo off
setlocal enabledelayedexpansion

echo [LOGICLENS] Looking for running LogicLens processes...

:: Check if we're in the project root
if exist "backend" (
    cd backend
    echo [LOGICLENS] Changed to backend directory
)

:: Check if virtual environment exists
if exist "venv" (
    echo [LOGICLENS] Activating virtual environment...
    call venv\Scripts\activate.bat
)

:: Create a shutdown log entry
echo [LOGICLENS] Creating shutdown log entry...
python -c "import sys; try: sys.path.append('.'); from app.utils.logger import get_logger; import platform, datetime, os; logger = get_logger('logiclens', {'store_logs': True}); logger.log_event(component='system', message='Application shutdown via shutdown script (Windows)', level='INFO', details={'timestamp': datetime.datetime.now().isoformat(), 'python_version': platform.python_version(), 'os': platform.system(), 'shutdown_type': 'manual'}); print('Shutdown log entry created successfully'); except Exception as e: print(f'Error creating shutdown log: {e}');"

:: Find Flask processes
for /f "tokens=1" %%p in ('tasklist /fi "IMAGENAME eq python.exe" /fo csv /nh ^| findstr /i "flask"') do (
    set FOUND=1
    echo [LOGICLENS] Found Flask process: %%p
    echo [LOGICLENS] Terminating process...
    taskkill /PID %%p /F
    if !errorlevel! equ 0 (
        echo [LOGICLENS] Process terminated successfully.
    ) else (
        echo [LOGICLENS] Failed to terminate process.
    )
)

:: Find LogicLens processes
for /f "tokens=1" %%p in ('tasklist /fi "IMAGENAME eq python.exe" /fo csv /nh ^| findstr /i "logiclens"') do (
    set FOUND=1
    echo [LOGICLENS] Found LogicLens process: %%p
    echo [LOGICLENS] Terminating process...
    taskkill /PID %%p /F
    if !errorlevel! equ 0 (
        echo [LOGICLENS] Process terminated successfully.
    ) else (
        echo [LOGICLENS] Failed to terminate process.
    )
)

:: Check if any processes were found
if not defined FOUND (
    echo [LOGICLENS] No LogicLens processes found running.
)

echo [LOGICLENS] Shutdown complete.

:: Optionally deactivate the virtual environment if it's active
if defined VIRTUAL_ENV (
    echo [LOGICLENS] Deactivating virtual environment...
    call deactivate
)

:: Change back to the original directory if needed
if "%CD%" == "%~dp0backend" (
    cd ..
)

endlocal 