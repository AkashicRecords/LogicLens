import random
from datetime import datetime, timedelta

class DummyDataGenerator:
    @staticmethod
    def generate_test_summary():
        return {
            'total_tests': random.randint(100, 500),
            'passed_tests': random.randint(80, 450),
            'failed_tests': random.randint(0, 20),
            'coverage': round(random.uniform(0.7, 0.95), 2),
            'test_duration': round(random.uniform(10, 300), 2),
            'last_run': (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat()
        }

    @staticmethod
    def generate_recent_logs():
        log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        log_types = ['TEST', 'SECURITY', 'PERFORMANCE', 'DEPLOYMENT']
        messages = [
            'Test suite completed successfully',
            'Security scan detected potential vulnerability',
            'Performance optimization completed',
            'New deployment initiated',
            'Database connection established',
            'Cache cleared successfully',
            'API endpoint response time increased',
            'Memory usage exceeded threshold',
            'Test coverage report generated',
            'Security patch applied'
        ]
        
        logs = []
        for _ in range(random.randint(5, 15)):
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, 60))
            logs.append({
                'timestamp': timestamp.isoformat(),
                'level': random.choice(log_levels),
                'type': random.choice(log_types),
                'message': random.choice(messages),
                'details': {
                    'component': random.choice(['frontend', 'backend', 'database', 'api']),
                    'trace_id': f"trace_{random.randint(1000, 9999)}"
                }
            })
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)

    @staticmethod
    def generate_analysis_data():
        return {
            'test_analysis': {
                'analysis': {
                    'coverage_score': round(random.uniform(0.7, 0.95), 2),
                    'coverage_issues': [
                        'Low coverage in authentication module',
                        'Missing integration tests for API endpoints',
                        'Incomplete test coverage for error handling'
                    ],
                    'performance_bottlenecks': [
                        'Slow database queries in user profile',
                        'Memory leak in image processing',
                        'High CPU usage in data aggregation'
                    ]
                }
            },
            'code_analysis': {
                'analysis': {
                    'quality_score': round(random.uniform(0.7, 0.95), 2),
                    'issues': [
                        'Complex function in data processing',
                        'Inconsistent error handling',
                        'Missing type hints'
                    ],
                    'performance_notes': [
                        'Consider caching for frequent queries',
                        'Optimize database connection pool',
                        'Implement lazy loading for large datasets'
                    ],
                    'improvements': [
                        'Refactor authentication logic',
                        'Add comprehensive error handling',
                        'Implement proper logging strategy'
                    ]
                }
            },
            'security_analysis': {
                'analysis': {
                    'security_score': round(random.uniform(0.7, 0.95), 2),
                    'vulnerabilities': [
                        'Potential SQL injection in user input',
                        'Missing CSRF protection',
                        'Insecure password storage'
                    ],
                    'owasp_compliance': {
                        'compliant': ['A1', 'A2', 'A3'],
                        'non_compliant': ['A4', 'A5']
                    },
                    'recommendations': [
                        'Implement input validation',
                        'Add rate limiting',
                        'Update security headers'
                    ]
                }
            }
        } 