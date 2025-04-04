# AI-Powered Logging and Testing Dashboard

A standalone application for monitoring and analyzing logs, tests, and code quality using AI-powered insights.

## Features

- Real-time log monitoring and analysis
- Test coverage and results visualization
- Security vulnerability detection
- Code quality metrics
- AI-powered chat interface for data analysis
- Interactive dashboard with visualizations
- Integration with DeepSeek R1 via OLLAMA

## System Requirements

### Minimum Requirements
- CPU: 4 cores
- RAM: 8GB
- Storage: 20GB
- GPU: Optional (CPU-only mode supported)

### Recommended Requirements
- CPU: 8+ cores
- RAM: 16GB+
- Storage: 50GB+
- GPU: NVIDIA GPU with 8GB+ VRAM

## Setup

### 1. OLLAMA Setup

#### Standard Installation
```bash
# Install OLLAMA
curl https://ollama.ai/install.sh | sh

# Pull DeepSeek R1 model
ollama pull deepseek-coder:r1

# Verify installation
ollama list
```

#### Low-Resource Installation
For systems with limited resources, use the quantized model:
```bash
# Pull quantized model (requires less VRAM)
ollama pull deepseek-coder:r1-q4_K_M
```

#### Performance Optimization
Add these environment variables for better performance:
```bash
# For NVIDIA GPUs
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_HOST=0.0.0.0
export OLLAMA_MODELS=/path/to/models

# For CPU-only systems
export OLLAMA_CPU_THREADS=4
export OLLAMA_GPU_LAYERS=0
```

### 2. Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your OLLAMA configuration
```

4. Run the Flask application:
```bash
flask run
```

The backend will be available at `http://localhost:5000`

### 3. Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## System Under Test (SUT) Integration

### 1. Log Collection
Add logging configuration to your SUT:

```python
# Example logging configuration
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger('sut')
    logger.setLevel(logging.INFO)
    
    # File handler
    handler = RotatingFileHandler(
        'logs/sut.log',
        maxBytes=10000000,
        backupCount=5
    )
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger
```

### 2. Test Integration
Configure your test framework to output results in a compatible format:

```python
# Example test configuration
import pytest
import json

def pytest_terminal_summary(terminalreporter):
    results = {
        'total_tests': terminalreporter._numcollected,
        'passed_tests': len(terminalreporter.stats.get('passed', [])),
        'failed_tests': len(terminalreporter.stats.get('failed', [])),
        'coverage': terminalreporter.stats.get('coverage', {}).get('total', 0)
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(results, f)
```

### 3. Security Scanning
Integrate security scanning tools:

```python
# Example security scan integration
from bandit import run_bandit

def run_security_scan():
    results = run_bandit(['-r', '.'])
    return {
        'vulnerabilities': results.get('vulnerabilities', []),
        'score': results.get('score', 0)
    }
```

### 4. Performance Monitoring
Add performance monitoring:

```python
# Example performance monitoring
import psutil
import time

def monitor_performance():
    metrics = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }
    return metrics
```

## API Integration

### 1. Log Analysis
```python
import requests

def analyze_logs(log_file):
    with open(log_file, 'r') as f:
        logs = f.read()
    
    response = requests.post(
        'http://localhost:5000/api/ai/analyze-logs',
        json={'logs': logs}
    )
    return response.json()
```

### 2. Test Analysis
```python
def analyze_tests(test_results):
    response = requests.post(
        'http://localhost:5000/api/ai/analyze-tests',
        json={'test_results': test_results}
    )
    return response.json()
```

### 3. Security Analysis
```python
def analyze_security(scan_results):
    response = requests.post(
        'http://localhost:5000/api/ai/analyze-security',
        json={'scan_results': scan_results}
    )
    return response.json()
```

## Usage

1. Open the dashboard in your browser
2. View real-time analysis of:
   - Security metrics
   - Code quality
   - Test coverage
   - Performance metrics

3. Use the chat interface to:
   - Ask questions about logs
   - Get test results
   - Request security analysis
   - Generate reports

## Demo Data

The application uses generated demo data for demonstration purposes. The data includes:
- Random test results
- Sample log entries
- Security analysis
- Code quality metrics
- Performance indicators

## API Endpoints

- `GET /api/ai/analysis`: Get comprehensive analysis data
- `POST /api/ai/chat`: Interact with the AI assistant
- `POST /api/ai/analyze-logs`: Analyze log files
- `POST /api/ai/analyze-tests`: Analyze test results
- `POST /api/ai/analyze-security`: Analyze security scan results

## Development

The application is structured as follows:
```
ai-logger/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   └── requirements.txt
└── frontend/
    └── src/
        └── components/
            └── AIDashboard/
```

## 🔧 Troubleshooting Guide

### Backend Issues

#### Flask Server Won't Start
1. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Port Already in Use**
   ```bash
   # Check what's using port 5000
   lsof -i :5000    # On Unix/Mac
   netstat -ano | findstr :5000  # On Windows
   ```

3. **Module Not Found Errors**
   ```bash
   # Verify all dependencies are installed
   pip install -r requirements.txt
   
   # If python-ollama fails, try:
   pip install python-ollama==0.2.4
   ```

### Frontend Issues

#### `npm start` Fails
1. **Node Modules Issues**
   ```bash
   # Clean install
   rm -rf node_modules
   rm package-lock.json
   npm install
   ```

2. **Port 3000 in Use**
   ```bash
   # Kill process using port 3000
   lsof -i :3000    # On Unix/Mac
   netstat -ano | findstr :3000  # On Windows
   ```

### OLLAMA Connection Issues

1. **Verify OLLAMA is Running**
   ```bash
   # Check OLLAMA status
   curl http://localhost:11434/api/version
   ```

2. **Common Error Messages and Solutions**:
   - "Connection refused": OLLAMA service not running
   - "Model not found": Need to pull the model first
   - "An error occurred": Check backend logs for details

### CORS Issues

1. **403 Forbidden Errors**
   - Check browser console for specific CORS errors
   - Verify frontend URL matches CORS configuration
   - Ensure all required headers are allowed

2. **API Connection Failed**
   - Confirm backend URL is correct in frontend config
   - Check if backend server is running
   - Verify network connectivity

### Environment Setup

1. **Environment Variables**
   ```bash
   # Backend (.env file)
   FLASK_APP=app
   FLASK_ENV=development
   
   # Frontend (.env file)
   REACT_APP_API_URL=http://localhost:5000
   ```

2. **File Permissions**
   ```bash
   # Fix permissions if needed
   chmod +x venv/bin/activate
   chmod -R 755 .
   ```

### Quick Verification Steps

1. Backend Health Check:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. Frontend Build Check:
   ```bash
   npm run build
   ```

3. OLLAMA Model Check:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Still Having Issues?

1. Check the logs:
   - Backend: Flask server output
   - Frontend: Browser console (F12)
   - OLLAMA: System logs

2. Common Root Causes:
   - Missing dependencies
   - Incorrect file permissions
   - Port conflicts
   - Network/firewall restrictions
   - Incompatible package versions

3. If problems persist:
   - Open an issue on GitHub
   - Include error messages and logs
   - Describe your environment setup
   - List steps to reproduce the issue 