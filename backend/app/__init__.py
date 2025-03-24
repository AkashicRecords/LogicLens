import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from .routes.ai_routes import ai_bp
from .utils.logger import get_logger
from .utils.test_utils import get_test_manager
from .utils.monitoring import get_monitoring_manager

# Load environment variables
load_dotenv()

def create_app(config=None):
    """
    Create and configure the Flask application
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Apply configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        API_KEY=os.environ.get('API_KEY', None),
        OLLAMA_HOST=os.environ.get('OLLAMA_HOST', 'http://localhost:11434'),
        OLLAMA_MODEL=os.environ.get('OLLAMA_MODEL', 'llama2'),
        LOG_LEVEL=os.environ.get('LOG_LEVEL', 'INFO'),
    )
    
    # Override with passed config if provided
    if config:
        app.config.update(config)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-API-Key"]
        }
    })
    
    # Initialize core services with app config
    logger = get_logger("logiclens", {
        "log_file": app.config.get("LOG_FILE"),
        "store_logs": True
    })
    
    test_manager = get_test_manager({
        "persist_results": app.config.get("PERSIST_TEST_RESULTS", False),
        "storage_dir": app.config.get("TEST_RESULTS_DIR", "test_results")
    })
    
    monitoring_manager = get_monitoring_manager({
        "persist_metrics": app.config.get("PERSIST_METRICS", False),
        "alert_thresholds": {
            "cpu_percent": app.config.get("CPU_ALERT_THRESHOLD", 90),
            "memory_percent": app.config.get("MEMORY_ALERT_THRESHOLD", 90),
            "disk_percent": app.config.get("DISK_ALERT_THRESHOLD", 90)
        }
    })
    
    # Collect initial metrics
    monitoring_manager.initialize()
    
    # Log application startup
    logger.log_event(
        component="app",
        message="LogicLens application starting",
        level="INFO",
        details={"mode": "web", "environment": os.environ.get("FLASK_ENV", "production")}
    )
    
    # Register blueprints
    app.register_blueprint(ai_bp, url_prefix='/api')
    
    # Register error handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        logger.log_event(
            component="app",
            message=f"Not Found: {request.path}",
            level="WARNING"
        )
        return jsonify({"error": "Not found"}), 404
        
    @app.errorhandler(500)
    def handle_server_error(e):
        logger.log_event(
            component="app",
            message=f"Server Error: {str(e)}",
            level="ERROR"
        )
        return jsonify({"error": "Internal server error"}), 500
    
    @app.before_request
    def check_api_key():
        if app.config["API_KEY"]:
            # Skip API key check for OPTIONS requests (CORS preflight)
            if request.method == 'OPTIONS':
                return None
                
            # Skip API key check for health endpoint
            if request.path == '/api/health':
                return None
                
            # Check API key for protected endpoints
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key != app.config["API_KEY"]:
                logger.log_event(
                    component="app",
                    message=f"Unauthorized API access attempt: {request.path}",
                    level="WARNING"
                )
                return jsonify({"error": "Unauthorized"}), 401
    
    return app 