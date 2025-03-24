from flask import Blueprint, jsonify, request
from datetime import datetime
import os

from ..services.ollama_service import OllamaService
from ..utils.logger import get_logger
from ..utils.test_utils import get_test_manager
from ..utils.monitoring import get_monitoring_manager

ai_bp = Blueprint('ai', __name__)

# Initialize services
ollama_service = OllamaService()
logger = get_logger()
test_manager = get_test_manager()
monitoring_manager = get_monitoring_manager()

@ai_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    })

@ai_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get recent logs"""
    component = request.args.get('component')
    level = request.args.get('level')
    limit = int(request.args.get('limit', 100))
    
    logs = logger.get_logs(
        filter_component=component,
        filter_level=level,
        limit=limit
    )
    
    return jsonify({
        "logs": logs,
        "total": len(logs)
    })

@ai_bp.route('/logs', methods=['POST'])
def add_log():
    """Add a new log entry"""
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    required_fields = ['component', 'message']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    log_entry = logger.log_event(
        component=data['component'],
        message=data['message'],
        level=data.get('level', 'INFO'),
        details=data.get('details')
    )
    
    return jsonify(log_entry)

@ai_bp.route('/logs/import', methods=['POST'])
def import_logs():
    """Import logs from external file"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400
        
    # Save file temporarily
    temp_path = f"/tmp/logiclens_import_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    file.save(temp_path)
    
    format_type = request.form.get('format', 'json')
    logs = logger.read_external_logs(temp_path, format_type)
    
    # Clean up
    os.remove(temp_path)
    
    return jsonify({
        "imported": len(logs),
        "logs": logs[:10]  # Return first 10 logs as preview
    })

@ai_bp.route('/tests/suites', methods=['GET'])
def get_test_suites():
    """Get all test suites"""
    suites = test_manager.get_all_suites()
    return jsonify({
        "suites": suites,
        "total": len(suites)
    })

@ai_bp.route('/tests/suites', methods=['POST'])
def create_test_suite():
    """Create a new test suite"""
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    suite_id = test_manager.start_suite(
        suite_id=data.get('id'),
        name=data.get('name', 'New Test Suite')
    )
    
    return jsonify({
        "suite_id": suite_id,
        "suite": test_manager.get_suite(suite_id)
    })

@ai_bp.route('/tests/suites/<suite_id>', methods=['GET'])
def get_test_suite(suite_id):
    """Get a specific test suite"""
    suite = test_manager.get_suite(suite_id)
    
    if not suite:
        return jsonify({"error": f"Test suite not found: {suite_id}"}), 404
        
    return jsonify(suite)

@ai_bp.route('/tests/suites/<suite_id>/results', methods=['POST'])
def add_test_result(suite_id):
    """Add a test result to a suite"""
    data = request.json
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    required_fields = ['test_id', 'name', 'status']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
            
    try:
        result = test_manager.add_test_result(
            suite_id=suite_id,
            test_id=data['test_id'],
            test_name=data['name'],
            status=data['status'],
            duration=data.get('duration', 0.0),
            message=data.get('message'),
            metadata=data.get('metadata')
        )
        
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@ai_bp.route('/tests/suites/<suite_id>/end', methods=['POST'])
def end_test_suite(suite_id):
    """End a test suite"""
    data = request.json or {}
    
    try:
        suite = test_manager.end_suite(
            suite_id=suite_id,
            status=data.get('status')
        )
        
        return jsonify(suite)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@ai_bp.route('/tests/import/junit', methods=['POST'])
def import_junit():
    """Import test results from JUnit XML"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400
        
    # Save file temporarily
    temp_path = f"/tmp/logiclens_junit_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
    file.save(temp_path)
    
    try:
        suite_name = request.form.get('name')
        suite_id = test_manager.import_junit_xml(temp_path, suite_name)
        suite = test_manager.get_suite(suite_id)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({
            "suite_id": suite_id,
            "suite": suite
        })
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({"error": str(e)}), 500

@ai_bp.route('/monitoring/metrics', methods=['GET'])
def get_metrics():
    """Get current system metrics"""
    # Collect fresh metrics
    metrics = monitoring_manager.collect_metrics()
    return jsonify(metrics)

@ai_bp.route('/monitoring/history', methods=['GET'])
def get_metrics_history():
    """Get metrics history"""
    count = int(request.args.get('count', 60))
    history = monitoring_manager.get_metrics_history(count)
    
    return jsonify({
        "metrics": history,
        "count": len(history)
    })

@ai_bp.route('/monitoring/system', methods=['GET'])
def get_system_info():
    """Get basic system information"""
    return jsonify(monitoring_manager.get_system_info())

@ai_bp.route('/monitoring/trends', methods=['GET'])
def analyze_metric_trend():
    """Analyze trends for a specific metric"""
    metric = request.args.get('metric')
    if not metric:
        return jsonify({"error": "No metric specified"}), 400
        
    window = int(request.args.get('window', 60))
    analysis = monitoring_manager.analyze_trends(metric, window)
    
    return jsonify(analysis)

@ai_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze data using OLLAMA
    """
    data = request.json
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400
    
    # Log the analysis request
    logger.log_event(
        component="ai_analysis",
        message=f"Analysis requested: {data['prompt'][:50]}...",
        level="INFO"
    )
    
    # Generate the response
    result = ollama_service.generate_response(
        data['prompt'],
        data.get('context')
    )
    
    # Log the result (success or failure)
    if 'error' in result:
        logger.log_event(
            component="ai_analysis",
            message=f"Analysis failed: {result['error']}",
            level="ERROR"
        )
    else:
        logger.log_event(
            component="ai_analysis",
            message="Analysis completed successfully",
            level="INFO"
        )
    
    return jsonify(result) 