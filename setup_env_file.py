#!/usr/bin/env python3
"""
Helper script to set up or update Ollama configuration in .env file
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def update_ollama_config(backend_dir, model=None, host=None):
    """
    Update the Ollama configuration in .env file
    
    Args:
        backend_dir: Path to the backend directory
        model: Ollama model to use (default: None, will not update)
        host: Ollama host to use (default: None, will not update)
    
    Returns:
        bool: True if successful, False otherwise
    """
    env_file = Path(backend_dir) / ".env"
    env_example = Path(backend_dir) / ".env.example"
    
    # Create .env from .env.example if it doesn't exist
    if not env_file.exists():
        if env_example.exists():
            print(f"Creating .env file from example...")
            with open(env_example, "r") as src:
                content = src.read()
            
            with open(env_file, "w") as dest:
                dest.write(content)
            
            print(".env file created")
        else:
            print(".env.example file not found", file=sys.stderr)
            return False
    
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
            if host:
                new_lines.append(f"OLLAMA_HOST={host}\n")
            else:
                new_lines.append(line)
        elif line.strip().startswith("OLLAMA_MODEL="):
            ollama_model_found = True
            if model:
                new_lines.append(f"OLLAMA_MODEL={model}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add settings if not found
    if not ollama_host_found and host:
        new_lines.append(f"OLLAMA_HOST={host}\n")
    
    if not ollama_model_found and model:
        new_lines.append(f"OLLAMA_MODEL={model}\n")
    
    # Write updated content
    with open(env_file, "w") as f:
        f.writelines(new_lines)
    
    print(f".env file updated with Ollama configuration")
    return True

def get_available_models():
    """
    Get available Ollama models
    
    Returns:
        list: List of available model names, or empty list if error
    """
    try:
        ollama_cmd = "ollama" if platform.system() != "Windows" else "ollama.exe"
        result = subprocess.run([ollama_cmd, "list"], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting available models: {result.stderr}", file=sys.stderr)
            return []
        
        # Parse output to extract model names
        models = []
        for line in result.stdout.strip().split("\n")[1:]:  # Skip header line
            if line.strip():
                parts = line.split()
                if parts:
                    models.append(parts[0])
        
        return models
    except Exception as e:
        print(f"Error listing models: {e}", file=sys.stderr)
        return []

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Ollama configuration in .env file")
    parser.add_argument("--backend-dir", default="backend", help="Path to backend directory")
    parser.add_argument("--host", help="Ollama host URL (e.g., http://localhost:11434)")
    parser.add_argument("--model", help="Ollama model name to use")
    parser.add_argument("--list-models", action="store_true", help="List available Ollama models")
    
    args = parser.parse_args()
    
    if args.list_models:
        print("Checking available Ollama models...")
        models = get_available_models()
        if models:
            print("Available models:")
            for model in models:
                print(f"  - {model}")
        else:
            print("No models available or Ollama not running")
        return
    
    update_ollama_config(args.backend_dir, args.model, args.host)

if __name__ == "__main__":
    main() 