"""
AutoPromptix Web Server

Flask web server providing API endpoints for test management and results visualization.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from .storage import StorageManager
from .prompt_improver import PromptImprover
from .test_runner import TestRunner, TestResult
from .decorators import get_test_registry, get_function_metadata

class AutoPromptixServer:
    """Web server for AutoPromptix"""
    
    def __init__(self, host='127.0.0.1', port=8000, 
                 api_model='gpt-4o-mini', max_test_n=10, 
                 prompt_modify_temperature=10):
        self.host = host
        self.port = port
        self.api_model = api_model
        self.max_test_n = max_test_n
        self.prompt_modify_temperature = prompt_modify_temperature
        
        # Initialize components
        self.storage = StorageManager()
        self.prompt_improver = PromptImprover(self.storage)
        self.test_runner = TestRunner(self.storage, self.prompt_improver)
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Add test callback for real-time updates
        self.test_runner.add_test_callback(self._on_test_complete)
        
        # Setup routes
        self._setup_routes()
        
        # Server state
        self.running = False
        self.server_thread = None
        self.active_tests = {}
        self.test_results_cache = {}
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/functions')
        def get_functions():
            """Get all registered functions"""
            registry = get_test_registry()
            functions = []
            
            for func_id, func_info in registry.items():
                metadata = func_info['metadata']
                stats = self.storage.get_function_stats(func_id)
                
                functions.append({
                    'id': func_id,
                    'name': func_id.split('.')[-1],
                    'module': func_id.split('.')[0],
                    'metadata': metadata,
                    'stats': stats
                })
            
            return jsonify({
                'functions': functions,
                'total': len(functions)
            })
        
        @self.app.route('/api/functions/<function_id>')
        def get_function(function_id):
            """Get details for a specific function"""
            registry = get_test_registry()
            if function_id not in registry:
                return jsonify({'error': 'Function not found'}), 404
            
            func_info = registry[function_id]
            metadata = func_info['metadata']
            stats = self.storage.get_function_stats(function_id)
            
            # Get recent test results
            recent_results = self.storage.get_test_results(function_id)[:10]
            
            # Get improvement history
            improvements = self.storage.get_prompt_improvements(function_id)[:5]
            
            return jsonify({
                'id': function_id,
                'name': function_id.split('.')[-1],
                'module': function_id.split('.')[0],
                'metadata': metadata,
                'stats': stats,
                'recent_results': recent_results,
                'improvements': improvements
            })
        
        @self.app.route('/api/functions/<function_id>/test', methods=['POST'])
        def run_test(function_id):
            """Run a test for a function"""
            data = request.get_json() or {}
            test_name = data.get('test_name', 'manual_test')
            prompt = data.get('prompt')
            config = data.get('config', {})
            
            try:
                result = self.test_runner.run_single_test(function_id, test_name, prompt, config)
                return jsonify({
                    'success': True,
                    'result': result.to_dict()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/functions/<function_id>/auto-test', methods=['POST'])
        def run_auto_test(function_id):
            """Run automated tests with improvements"""
            data = request.get_json() or {}
            max_iterations = data.get('max_iterations', self.max_test_n)
            
            # Run tests in background
            def run_tests():
                try:
                    results = self.test_runner.run_automated_tests(function_id, max_iterations)
                    self.test_results_cache[function_id] = results
                    self.active_tests[function_id] = {
                        'status': 'completed',
                        'results': len(results),
                        'completed_at': datetime.now().isoformat()
                    }
                except Exception as e:
                    self.active_tests[function_id] = {
                        'status': 'failed',
                        'error': str(e),
                        'completed_at': datetime.now().isoformat()
                    }
            
            # Start background test
            self.active_tests[function_id] = {
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'max_iterations': max_iterations
            }
            
            thread = threading.Thread(target=run_tests)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'success': True,
                'message': 'Automated tests started',
                'test_id': function_id
            })
        
        @self.app.route('/api/functions/<function_id>/test-status')
        def get_test_status(function_id):
            """Get test status for a function"""
            status = self.active_tests.get(function_id, {'status': 'idle'})
            return jsonify(status)
        
        @self.app.route('/api/functions/<function_id>/results')
        def get_test_results(function_id):
            """Get test results for a function"""
            limit = request.args.get('limit', 50, type=int)
            results = self.storage.get_test_results(function_id)[:limit]
            
            return jsonify({
                'results': results,
                'total': len(results)
            })
        
        @self.app.route('/api/functions/<function_id>/improvements')
        def get_improvements(function_id):
            """Get prompt improvements for a function"""
            improvements = self.storage.get_prompt_improvements(function_id)
            return jsonify({
                'improvements': improvements,
                'total': len(improvements)
            })
        
        @self.app.route('/api/functions/<function_id>/analyze-prompt', methods=['POST'])
        def analyze_prompt(function_id):
            """Analyze a prompt for a function"""
            data = request.get_json() or {}
            prompt = data.get('prompt', '')
            
            if not prompt:
                return jsonify({'error': 'Prompt is required'}), 400
            
            try:
                analysis = self.prompt_improver.analyze_prompt(prompt)
                return jsonify({
                    'analysis': {
                        'clarity_score': analysis.clarity_score,
                        'specificity_score': analysis.specificity_score,
                        'completeness_score': analysis.completeness_score,
                        'potential_issues': analysis.potential_issues,
                        'suggested_improvements': analysis.suggested_improvements
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/functions/<function_id>/improve-prompt', methods=['POST'])
        def improve_prompt(function_id):
            """Improve a prompt for a function"""
            data = request.get_json() or {}
            prompt = data.get('prompt', '')
            improvement_type = data.get('improvement_type', 'auto')
            
            if not prompt:
                return jsonify({'error': 'Prompt is required'}), 400
            
            try:
                # Get recent test results for context
                recent_results = self.storage.get_test_results(function_id)[:5]
                
                improvement = self.prompt_improver.improve_prompt(
                    function_id, prompt, recent_results, improvement_type
                )
                
                return jsonify({
                    'improvement': {
                        'original_prompt': improvement.original_prompt,
                        'improved_prompt': improvement.improved_prompt,
                        'improvement_reason': improvement.improvement_reason,
                        'confidence_score': improvement.confidence_score,
                        'expected_performance_gain': improvement.expected_performance_gain
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get overall statistics"""
            registry = get_test_registry()
            total_functions = len(registry)
            
            # Get aggregate stats
            all_results = []
            for func_id in registry.keys():
                results = self.storage.get_test_results(func_id)
                all_results.extend(results)
            
            total_tests = len(all_results)
            avg_score = sum(r.get('score', 0) for r in all_results) / total_tests if total_tests > 0 else 0
            
            return jsonify({
                'total_functions': total_functions,
                'total_tests': total_tests,
                'avg_score': avg_score,
                'active_tests': len([t for t in self.active_tests.values() if t['status'] == 'running'])
            })
        
        @self.app.route('/api/settings')
        def get_settings():
            """Get current settings"""
            return jsonify({
                'host': self.host,
                'port': self.port,
                'api_model': self.api_model,
                'max_test_n': self.max_test_n,
                'prompt_modify_temperature': self.prompt_modify_temperature
            })
        
        @self.app.route('/api/settings', methods=['POST'])
        def update_settings():
            """Update settings"""
            data = request.get_json() or {}
            
            if 'api_model' in data:
                self.api_model = data['api_model']
            if 'max_test_n' in data:
                self.max_test_n = data['max_test_n']
            if 'prompt_modify_temperature' in data:
                self.prompt_modify_temperature = data['prompt_modify_temperature']
            
            return jsonify({'success': True, 'message': 'Settings updated'})
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '0.1.0'
            })
    
    def _on_test_complete(self, result: TestResult):
        """Callback when a test completes"""
        # Update cache or send real-time updates
        print(f"Test completed: {result.function_id} - {result.test_name} - Score: {result.score}")
    
    def start(self):
        """Start the web server"""
        if self.running:
            return False
        
        self.running = True
        
        def run_server():
            self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"AutoPromptix server started at http://{self.host}:{self.port}")
        return True
    
    def stop(self):
        """Stop the web server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=1)
        print("AutoPromptix server stopped")

# HTML Template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoPromptix Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-item { background: #007bff; color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; }
        .stat-label { margin-top: 5px; }
        .functions-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .function-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: white; }
        .function-title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .function-meta { color: #666; margin-bottom: 10px; }
        .function-stats { display: flex; justify-content: space-between; margin-bottom: 15px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .loading { text-align: center; padding: 20px; }
        .error { color: red; padding: 10px; background: #ffebee; border-radius: 4px; }
        .success { color: green; padding: 10px; background: #e8f5e8; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AutoPromptix Dashboard</h1>
            <p>Automated Prompt Testing and Improvement</p>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-item">
                <div class="stat-value" id="total-functions">0</div>
                <div class="stat-label">Functions</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="total-tests">0</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="avg-score">0.0</div>
                <div class="stat-label">Avg Score</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" id="active-tests">0</div>
                <div class="stat-label">Active Tests</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Registered Functions</h2>
            <div id="functions-container" class="loading">
                Loading functions...
            </div>
        </div>
    </div>
    
    <script>
        // Load dashboard data
        async function loadDashboard() {
            try {
                const [statsResponse, functionsResponse] = await Promise.all([
                    fetch('/api/stats'),
                    fetch('/api/functions')
                ]);
                
                const stats = await statsResponse.json();
                const functions = await functionsResponse.json();
                
                updateStats(stats);
                updateFunctions(functions.functions);
            } catch (error) {
                console.error('Error loading dashboard:', error);
                document.getElementById('functions-container').innerHTML = 
                    '<div class="error">Error loading dashboard data</div>';
            }
        }
        
        function updateStats(stats) {
            document.getElementById('total-functions').textContent = stats.total_functions;
            document.getElementById('total-tests').textContent = stats.total_tests;
            document.getElementById('avg-score').textContent = stats.avg_score.toFixed(2);
            document.getElementById('active-tests').textContent = stats.active_tests;
        }
        
        function updateFunctions(functions) {
            const container = document.getElementById('functions-container');
            
            if (functions.length === 0) {
                container.innerHTML = '<p>No functions registered yet. Add @autopromptix decorators to your functions.</p>';
                return;
            }
            
            container.innerHTML = '<div class="functions-grid">' + 
                functions.map(func => `
                    <div class="function-card">
                        <div class="function-title">${func.name}</div>
                        <div class="function-meta">${func.module}</div>
                        <div class="function-stats">
                            <span>Tests: ${func.stats.test_count}</span>
                            <span>Score: ${func.stats.avg_score.toFixed(2)}</span>
                        </div>
                        <div>
                            <button class="btn btn-primary" onclick="runTest('${func.id}')">Run Test</button>
                            <button class="btn btn-success" onclick="runAutoTest('${func.id}')">Auto Test</button>
                        </div>
                    </div>
                `).join('') +
                '</div>';
        }
        
        async function runTest(functionId) {
            try {
                const response = await fetch(`/api/functions/${functionId}/test`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ test_name: 'manual_test' })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert(`Test completed! Score: ${result.result.score.toFixed(2)}`);
                } else {
                    alert(`Test failed: ${result.error}`);
                }
            } catch (error) {
                alert(`Error running test: ${error.message}`);
            }
        }
        
        async function runAutoTest(functionId) {
            try {
                const response = await fetch(`/api/functions/${functionId}/auto-test`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ max_iterations: 5 })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Automated tests started! Check back in a few minutes.');
                } else {
                    alert(`Failed to start tests: ${result.error}`);
                }
            } catch (error) {
                alert(`Error starting auto tests: ${error.message}`);
            }
        }
        
        // Load dashboard on page load
        loadDashboard();
        
        // Refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
""" 