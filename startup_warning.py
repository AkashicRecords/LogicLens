#!/usr/bin/env python3
"""
Flask Server Startup Warning Script

This script intercepts manual flask run commands and warns the user to use
the management script instead. It's designed to prevent common startup errors.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path


def print_warning():
    """Print a very visible warning message"""
    print("\n" + "!" * 80)
    print("!! MANUAL STARTUP DETECTED - THIS IS THE WRONG WAY TO START THE SERVER !!")
    print("!" * 80)
    print("\nManual flask commands frequently cause these errors:")
    print("  1. Command not found: python (use python3 instead)")
    print("  2. No module named flask (virtual environment not activated)")
    print("  3. Port already in use (previous instance not properly stopped)")
    print("  4. Dependencies installed in wrong location")
    print("\nINSTEAD, please use the management script:")
    print("\n    python3 logiclens_manage.py start\n")
    print("This script will:")
    print("  - Check for and stop any running instances")
    print("  - Create and activate the virtual environment")
    print("  - Install dependencies in the correct location")
    print("  - Start the server with the proper configuration")
    print("\nTo stop the server, use:")
    print("\n    python3 logiclens_manage.py stop\n")
    print("!" * 80 + "\n")


def check_manage_script_exists():
    """Check if logiclens_manage.py exists in the current or parent directory"""
    current_dir = Path.cwd()
    
    # Check current directory
    if (current_dir / "logiclens_manage.py").exists():
        return True
    
    # Check parent directory
    if (current_dir.parent / "logiclens_manage.py").exists():
        return True
        
    return False


def is_flask_command(args):
    """Check if the command is a Flask run command"""
    if len(args) < 2:
        return False
    
    cmd = " ".join(args)
    flask_patterns = [
        "flask run", 
        "-m flask run",
        "flask.run",
        "app.run"
    ]
    
    return any(pattern in cmd for pattern in flask_patterns)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        return
    
    # Check if this looks like a Flask run command
    if is_flask_command(sys.argv[1:]):
        if check_manage_script_exists():
            print_warning()
            
            # Ask user if they want to run the management script instead
            response = input("Would you like to use the management script instead? (y/n): ")
            if response.lower().startswith('y'):
                # Get python command (python or python3)
                python_cmd = "python3" if shutil.which("python3") else "python"
                
                # Find the directory with logiclens_manage.py
                current_dir = Path.cwd()
                if (current_dir / "logiclens_manage.py").exists():
                    manage_path = current_dir / "logiclens_manage.py"
                elif (current_dir.parent / "logiclens_manage.py").exists():
                    manage_path = current_dir.parent / "logiclens_manage.py"
                    os.chdir(current_dir.parent)
                else:
                    print("Could not find logiclens_manage.py")
                    return
                
                # Run the management script
                print(f"Running {python_cmd} {manage_path} start...")
                subprocess.run([python_cmd, str(manage_path), "start"])
                sys.exit(0)
            else:
                print("\nContinuing with manual method (not recommended).\n")
                # Continue with original command


if __name__ == "__main__":
    main() 