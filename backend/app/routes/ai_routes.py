from flask import Blueprint, jsonify, request
from ..utils.dummy_data import DummyDataGenerator
from ..services.ollama_service import OllamaService

ai_bp = Blueprint('ai', __name__)
dummy_data = DummyDataGenerator()
ollama_service = OllamaService()

@ai_bp.route('/api/ai/analysis', methods=['GET'])
def get_analysis():
    """Get comprehensive AI analysis of the codebase"""
    try:
        return jsonify(dummy_data.generate_analysis_data())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ai_bp.route('/api/ai/chat', methods=['POST'])
def chat():
    """Handle chat interactions with AI"""
    try:
        data = request.json
        message = data.get('message')
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
            
        # Get relevant context based on the message
        context_data = {}
        
        # Check if the message is about logs
        if any(keyword in message.lower() for keyword in ['log', 'logs', 'logging']):
            context_data['logs'] = dummy_data.generate_recent_logs()
            
        # Check if the message is about tests
        if any(keyword in message.lower() for keyword in ['test', 'tests', 'testing', 'coverage']):
            context_data['test_results'] = dummy_data.generate_test_summary()
            
        # Generate a contextual response
        response = generate_chat_response(message, context_data)
        
        return jsonify({
            'response': response,
            'context': context_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_chat_response(message, context):
    """Generate a contextual response based on the message and available data"""
    message_lower = message.lower()
    
    if any(keyword in message_lower for keyword in ['log', 'logs', 'logging']):
        logs = context.get('logs', [])
        if logs:
            recent_logs = logs[:3]
            return f"Here are the 3 most recent logs:\n" + "\n".join(
                f"- [{log['timestamp']}] {log['level']}: {log['message']}"
                for log in recent_logs
            )
        return "No recent logs available."
        
    elif any(keyword in message_lower for keyword in ['test', 'tests', 'testing', 'coverage']):
        test_results = context.get('test_results', {})
        if test_results:
            return f"Test Summary:\n" + \
                   f"- Total Tests: {test_results['total_tests']}\n" + \
                   f"- Passed: {test_results['passed_tests']}\n" + \
                   f"- Failed: {test_results['failed_tests']}\n" + \
                   f"- Coverage: {test_results['coverage']*100}%\n" + \
                   f"- Last Run: {test_results['last_run']}"
        return "No test results available."
        
    elif any(keyword in message_lower for keyword in ['security', 'vulnerability']):
        return "Security Analysis:\n" + \
               "- Recent security scan completed\n" + \
               "- 3 potential vulnerabilities detected\n" + \
               "- Recommendations available in the dashboard"
               
    elif any(keyword in message_lower for keyword in ['performance', 'speed']):
        return "Performance Analysis:\n" + \
               "- Database queries optimization needed\n" + \
               "- Memory usage within acceptable range\n" + \
               "- API response times stable"
               
    else:
        return "I can help you with:\n" + \
               "- Log analysis\n" + \
               "- Test results\n" + \
               "- Security analysis\n" + \
               "- Performance metrics\n" + \
               "What would you like to know more about?"

@ai_bp.route('/analyze-logs', methods=['POST'])
def analyze_logs():
    """
    Analyze logs using OLLAMA
    """
    data = request.get_json()
    if not data or 'logs' not in data:
        return jsonify({"error": "No logs provided"}), 400
    
    result = ollama_service.analyze_logs(data['logs'])
    return jsonify(result)

@ai_bp.route('/analyze-tests', methods=['POST'])
def analyze_tests():
    """
    Analyze test results using OLLAMA
    """
    data = request.get_json()
    if not data or 'test_results' not in data:
        return jsonify({"error": "No test results provided"}), 400
    
    result = ollama_service.analyze_tests(data['test_results'])
    return jsonify(result)

@ai_bp.route('/analyze-security', methods=['POST'])
def analyze_security():
    """
    Analyze security data using OLLAMA
    """
    data = request.get_json()
    if not data or 'security_data' not in data:
        return jsonify({"error": "No security data provided"}), 400
    
    result = ollama_service.analyze_security(data['security_data'])
    return jsonify(result)

@ai_bp.route('/generate', methods=['POST'])
def generate():
    """
    Generate a response using OLLAMA
    """
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "No prompt provided"}), 400
    
    result = ollama_service.generate_response(
        data['prompt'],
        data.get('context')
    )
    return jsonify(result) 