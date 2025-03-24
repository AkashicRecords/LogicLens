import os
import requests
from typing import Dict, Any

class OllamaService:
    def __init__(self):
        self.base_url = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = 'deepseek-coder:r1'  # Default model

    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a response using the OLLAMA API
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "context": context or {}
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def analyze_logs(self, logs: str) -> Dict[str, Any]:
        """
        Analyze logs using OLLAMA
        """
        prompt = f"""Analyze the following logs and provide insights:
        
        {logs}
        
        Please provide:
        1. Key issues or errors
        2. Performance metrics
        3. Security concerns
        4. Recommendations
        """
        
        return self.generate_response(prompt)

    def analyze_tests(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test results using OLLAMA
        """
        prompt = f"""Analyze the following test results and provide insights:
        
        {test_results}
        
        Please provide:
        1. Test coverage analysis
        2. Failed test patterns
        3. Performance bottlenecks
        4. Recommendations for improvement
        """
        
        return self.generate_response(prompt)

    def analyze_security(self, security_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze security data using OLLAMA
        """
        prompt = f"""Analyze the following security data and provide insights:
        
        {security_data}
        
        Please provide:
        1. Security vulnerabilities
        2. Risk assessment
        3. Compliance issues
        4. Recommendations for improvement
        """
        
        return self.generate_response(prompt) 