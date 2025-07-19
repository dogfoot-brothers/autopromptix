"""
Enhanced AutoPromptix Web Server

Improved web server with better dashboard and real-time prompt editing.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from .storage import StorageManager
from .prompt_improver import PromptImprover
from .test_runner import TestRunner, TestResult
from .enhanced_decorators import get_test_registry, get_function_metadata

class EnhancedAutoPromptixServer:
    """Enhanced web server for AutoPromptix with improved dashboard"""
    
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
            """Enhanced main dashboard page"""
            return render_template_string(ENHANCED_DASHBOARD_TEMPLATE)
        
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
        
        @self.app.route('/api/functions/<function_id>/prompt-editor', methods=['GET'])
        def get_prompt_editor(function_id):
            """Get prompt editor interface"""
            registry = get_test_registry()
            if function_id not in registry:
                return jsonify({'error': 'Function not found'}), 404
            
            func_info = registry[function_id]
            metadata = func_info['metadata']
            
            # Extract current prompt from function
            current_prompt = self._extract_current_prompt(func_info)
            
            return jsonify({
                'function_id': function_id,
                'current_prompt': current_prompt,
                'metadata': metadata,
                'prompt_variations': metadata.get('prompt_variations', [])
            })
        
        @self.app.route('/api/functions/<function_id>/prompt-editor', methods=['POST'])
        def update_prompt(function_id):
            """Update prompt for a function"""
            data = request.get_json() or {}
            new_prompt = data.get('prompt')
            
            if not new_prompt:
                return jsonify({'error': 'Prompt is required'}), 400
            
            try:
                # Store the new prompt
                self.storage.save_knowledge(
                    function_id, 
                    'current_prompt', 
                    new_prompt,
                    {'updated_at': datetime.now().isoformat()}
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Prompt updated successfully'
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/functions/<function_id>/ab-test', methods=['POST'])
        def run_ab_test(function_id):
            """Run A/B test between prompt variants"""
            data = request.get_json() or {}
            prompt_a = data.get('prompt_a')
            prompt_b = data.get('prompt_b')
            num_tests = data.get('num_tests', 5)
            
            if not prompt_a or not prompt_b:
                return jsonify({'error': 'Both prompts are required'}), 400
            
            try:
                results_a = []
                results_b = []
                
                # Run tests for prompt A
                for i in range(num_tests):
                    result_a = self.test_runner.run_single_test(
                        function_id, f'ab_test_a_{i}', prompt_a
                    )
                    results_a.append(result_a.score)
                
                # Run tests for prompt B
                for i in range(num_tests):
                    result_b = self.test_runner.run_single_test(
                        function_id, f'ab_test_b_{i}', prompt_b
                    )
                    results_b.append(result_b.score)
                
                avg_a = sum(results_a) / len(results_a)
                avg_b = sum(results_b) / len(results_b)
                
                winner = 'A' if avg_a > avg_b else 'B'
                
                return jsonify({
                    'success': True,
                    'results': {
                        'prompt_a': {
                            'prompt': prompt_a,
                            'scores': results_a,
                            'average': avg_a
                        },
                        'prompt_b': {
                            'prompt': prompt_b,
                            'scores': results_b,
                            'average': avg_b
                        },
                        'winner': winner,
                        'difference': abs(avg_a - avg_b)
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
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
                'version': '0.2.0'
            })
    
    def _extract_current_prompt(self, function_info: Dict[str, Any]) -> str:
        """Extract current prompt from function info"""
        # Try to find prompt in function source code
        func = function_info['function']
        source_code = self._get_function_source(func)
        
        # Look for system prompt in common patterns
        prompt_patterns = [
            r'system.*?content.*?["\']([^"\']+)["\']',
            r'prompt\s*=\s*["\']([^"\']+)["\']',
            r'system_prompt\s*=\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in prompt_patterns:
            import re
            match = re.search(pattern, source_code, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        # Default prompt if none found
        return "You are a helpful assistant."
    
    def _get_function_source(self, func: Callable) -> str:
        """Get source code of a function"""
        try:
            import inspect
            return inspect.getsource(func)
        except:
            return ""
    
    def _on_test_complete(self, result: TestResult):
        """Callback when a test completes"""
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
        
        print(f"Enhanced AutoPromptix server started at http://{self.host}:{self.port}")
        return True
    
    def stop(self):
        """Stop the web server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=1)
        print("Enhanced AutoPromptix server stopped")

# Enhanced HTML Template for the dashboard
ENHANCED_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced AutoPromptix Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px;
        }
        .header { 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 30px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .header h1 { 
            color: #4a5568; 
            font-size: 2.5em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p { 
            color: #718096; 
            font-size: 1.1em;
        }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 25px; 
            margin-bottom: 30px; 
        }
        .stat-item { 
            background: rgba(255,255,255,0.95); 
            padding: 25px; 
            border-radius: 15px; 
            text-align: center; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }
        .stat-item:hover {
            transform: translateY(-5px);
        }
        .stat-value { 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-label { 
            color: #718096; 
            font-size: 1.1em;
            font-weight: 500;
        }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        .card { 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        .card h2 { 
            color: #4a5568; 
            margin-bottom: 20px;
            font-size: 1.5em;
        }
        .functions-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 20px; 
        }
        .function-card { 
            border: 2px solid #e2e8f0; 
            border-radius: 12px; 
            padding: 20px; 
            background: white;
            transition: all 0.3s ease;
        }
        .function-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
        }
        .function-title { 
            font-size: 1.3em; 
            font-weight: bold; 
            margin-bottom: 10px;
            color: #4a5568;
        }
        .function-meta { 
            color: #718096; 
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        .function-stats { 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 20px;
            padding: 10px;
            background: #f7fafc;
            border-radius: 8px;
        }
        .btn { 
            padding: 10px 20px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            margin-right: 10px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .btn-primary { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-success { 
            background: linear-gradient(45deg, #48bb78, #38a169); 
            color: white; 
        }
        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
        }
        .btn-warning { 
            background: linear-gradient(45deg, #ed8936, #dd6b20); 
            color: white; 
        }
        .btn-warning:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(237, 137, 54, 0.4);
        }
        .prompt-editor {
            background: #f7fafc;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .prompt-textarea {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s ease;
        }
        .prompt-textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .editor-toolbar {
            margin-top: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .loading { 
            text-align: center; 
            padding: 40px; 
            color: #718096;
        }
        .error { 
            color: #e53e3e; 
            padding: 15px; 
            background: #fed7d7; 
            border-radius: 8px; 
            margin: 10px 0;
        }
        .success { 
            color: #38a169; 
            padding: 15px; 
            background: #c6f6d5; 
            border-radius: 8px; 
            margin: 10px 0;
        }
        .test-results {
            margin-top: 20px;
        }
        .result-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        .score {
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }
        .output {
            margin-top: 10px;
            padding: 10px;
            background: #f7fafc;
            border-radius: 4px;
            font-family: monospace;
        }
        .ab-test-dashboard {
            margin-top: 20px;
        }
        .test-variants {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .variant {
            background: white;
            border-radius: 8px;
            padding: 20px;
            border: 2px solid #e2e8f0;
        }
        .variant.winner {
            border-color: #48bb78;
            background: #f0fff4;
        }
        .metrics {
            margin-top: 15px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        .metric:last-child {
            border-bottom: none;
        }
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            .test-variants {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced AutoPromptix Dashboard</h1>
            <p>Advanced Prompt Testing and Improvement Platform</p>
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
        
        <div class="main-content">
            <div class="card">
                <h2>📋 Registered Functions</h2>
                <div id="functions-container" class="loading">
                    Loading functions...
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Prompt Editor</h2>
                <div id="prompt-editor-container">
                    <p>Select a function to edit its prompt</p>
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 30px;">
            <h2>🧪 A/B Testing</h2>
            <div id="ab-test-container">
                <p>Select a function to run A/B tests</p>
            </div>
        </div>
    </div>
    
    <script>
        let currentFunction = null;
        
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
                            <button class="btn btn-warning" onclick="openPromptEditor('${func.id}')">Edit Prompt</button>
                        </div>
                    </div>
                `).join('') +
                '</div>';
        }
        
        async function openPromptEditor(functionId) {
            try {
                const response = await fetch(`/api/functions/${functionId}/prompt-editor`);
                const data = await response.json();
                
                currentFunction = functionId;
                
                document.getElementById('prompt-editor-container').innerHTML = `
                    <div class="prompt-editor">
                        <h3>Editing: ${data.function_id}</h3>
                        <textarea id="prompt-textarea" class="prompt-textarea">${data.current_prompt}</textarea>
                        <div class="editor-toolbar">
                            <button class="btn btn-primary" onclick="testPrompt()">Test Prompt</button>
                            <button class="btn btn-success" onclick="savePrompt()">Save Prompt</button>
                            <button class="btn btn-warning" onclick="improvePrompt()">Improve Prompt</button>
                        </div>
                        <div id="prompt-results"></div>
                    </div>
                `;
                
                // Load A/B test interface
                loadABTestInterface(functionId);
                
            } catch (error) {
                console.error('Error opening prompt editor:', error);
            }
        }
        
        async function testPrompt() {
            if (!currentFunction) return;
            
            const prompt = document.getElementById('prompt-textarea').value;
            const resultsDiv = document.getElementById('prompt-results');
            
            try {
                resultsDiv.innerHTML = '<div class="loading">Testing prompt...</div>';
                
                const response = await fetch(`/api/functions/${currentFunction}/test`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        test_name: 'prompt_editor_test',
                        prompt: prompt
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultsDiv.innerHTML = `
                        <div class="result-card">
                            <div class="score">Score: ${result.result.score.toFixed(3)}</div>
                            <div class="output">Output: ${result.result.actual_output}</div>
                        </div>
                    `;
                } else {
                    resultsDiv.innerHTML = `<div class="error">Test failed: ${result.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function savePrompt() {
            if (!currentFunction) return;
            
            const prompt = document.getElementById('prompt-textarea').value;
            
            try {
                const response = await fetch(`/api/functions/${currentFunction}/prompt-editor`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('prompt-results').innerHTML = 
                        '<div class="success">Prompt saved successfully!</div>';
                } else {
                    document.getElementById('prompt-results').innerHTML = 
                        `<div class="error">Failed to save: ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('prompt-results').innerHTML = 
                    `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function improvePrompt() {
            if (!currentFunction) return;
            
            const prompt = document.getElementById('prompt-textarea').value;
            const resultsDiv = document.getElementById('prompt-results');
            
            try {
                resultsDiv.innerHTML = '<div class="loading">Improving prompt...</div>';
                
                const response = await fetch(`/api/functions/${currentFunction}/improve-prompt`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt })
                });
                
                const result = await response.json();
                
                if (result.improvement) {
                    document.getElementById('prompt-textarea').value = result.improvement.improved_prompt;
                    resultsDiv.innerHTML = `
                        <div class="success">
                            <h4>Prompt Improved!</h4>
                            <p><strong>Reason:</strong> ${result.improvement.improvement_reason}</p>
                            <p><strong>Confidence:</strong> ${(result.improvement.confidence_score * 100).toFixed(1)}%</p>
                        </div>
                    `;
                } else {
                    resultsDiv.innerHTML = `<div class="error">Failed to improve: ${result.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        async function loadABTestInterface(functionId) {
            const container = document.getElementById('ab-test-container');
            
            container.innerHTML = `
                <h3>A/B Test for: ${functionId}</h3>
                <div class="test-variants">
                    <div class="variant">
                        <h4>Variant A</h4>
                        <textarea id="prompt-a" class="prompt-textarea" placeholder="Enter prompt variant A..."></textarea>
                        <div class="metrics" id="metrics-a">
                            <div class="metric">Score: -</div>
                            <div class="metric">Tests: -</div>
                        </div>
                    </div>
                    
                    <div class="variant">
                        <h4>Variant B</h4>
                        <textarea id="prompt-b" class="prompt-textarea" placeholder="Enter prompt variant B..."></textarea>
                        <div class="metrics" id="metrics-b">
                            <div class="metric">Score: -</div>
                            <div class="metric">Tests: -</div>
                        </div>
                    </div>
                </div>
                
                <div class="editor-toolbar">
                    <button class="btn btn-primary" onclick="runABTest()">Run A/B Test</button>
                    <button class="btn btn-success" onclick="clearABTest()">Clear Results</button>
                </div>
                
                <div id="ab-test-results"></div>
            `;
        }
        
        async function runABTest() {
            if (!currentFunction) return;
            
            const promptA = document.getElementById('prompt-a').value;
            const promptB = document.getElementById('prompt-b').value;
            const resultsDiv = document.getElementById('ab-test-results');
            
            if (!promptA || !promptB) {
                resultsDiv.innerHTML = '<div class="error">Please enter both prompt variants</div>';
                return;
            }
            
            try {
                resultsDiv.innerHTML = '<div class="loading">Running A/B test...</div>';
                
                const response = await fetch(`/api/functions/${currentFunction}/ab-test`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        prompt_a: promptA,
                        prompt_b: promptB,
                        num_tests: 5
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const data = result.results;
                    
                    // Update metrics
                    document.getElementById('metrics-a').innerHTML = `
                        <div class="metric">Score: ${data.prompt_a.average.toFixed(3)}</div>
                        <div class="metric">Tests: ${data.prompt_a.scores.length}</div>
                    `;
                    
                    document.getElementById('metrics-b').innerHTML = `
                        <div class="metric">Score: ${data.prompt_b.average.toFixed(3)}</div>
                        <div class="metric">Tests: ${data.prompt_b.scores.length}</div>
                    `;
                    
                    // Highlight winner
                    document.querySelectorAll('.variant').forEach(v => v.classList.remove('winner'));
                    if (data.winner === 'A') {
                        document.querySelector('.variant:first-child').classList.add('winner');
                    } else {
                        document.querySelector('.variant:last-child').classList.add('winner');
                    }
                    
                    resultsDiv.innerHTML = `
                        <div class="success">
                            <h4>A/B Test Complete!</h4>
                            <p><strong>Winner:</strong> Variant ${data.winner}</p>
                            <p><strong>Difference:</strong> ${(data.difference * 100).toFixed(1)}%</p>
                        </div>
                    `;
                } else {
                    resultsDiv.innerHTML = `<div class="error">A/B test failed: ${result.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        function clearABTest() {
            document.getElementById('prompt-a').value = '';
            document.getElementById('prompt-b').value = '';
            document.getElementById('metrics-a').innerHTML = `
                <div class="metric">Score: -</div>
                <div class="metric">Tests: -</div>
            `;
            document.getElementById('metrics-b').innerHTML = `
                <div class="metric">Score: -</div>
                <div class="metric">Tests: -</div>
            `;
            document.getElementById('ab-test-results').innerHTML = '';
            document.querySelectorAll('.variant').forEach(v => v.classList.remove('winner'));
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
                    alert(`Test completed! Score: ${result.result.score.toFixed(3)}`);
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