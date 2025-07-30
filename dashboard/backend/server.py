"""
AutoPromptix Dashboard Backend Server

Flask API server for AutoPromptix dashboard with Test Data Pool management.
"""

from flask import Flask, request, jsonify, send_from_directory, send_file, make_response
from flask_cors import CORS
import json
import threading
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import AutoPromptix components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from autopromptix.storage import StorageManager
from autopromptix.prompt_improver import PromptImprover
from autopromptix.test_runner import TestRunner, TestResult
from autopromptix.decorators import get_test_registry, get_function_metadata
from autopromptix.test_data_pool import TestDataPoolManager, TestDataPool, TestCase

class DashboardServer:
    """Dashboard backend server for AutoPromptix"""
    
    def __init__(self, host='127.0.0.1', port=8001):
        self.host = host
        self.port = port
        
        # Initialize components
        self.storage = StorageManager()
        self.prompt_improver = PromptImprover(self.storage)
        self.test_runner = TestRunner(self.storage, self.prompt_improver)
        self.test_data_manager = TestDataPoolManager()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Setup routes
        self._setup_routes()
        
        # Server state
        self.running = False
        self.server_thread = None
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        # Frontend directory removed - using built-in HTML dashboard
        
        @self.app.route('/')
        def index():
            """Serve the dashboard page"""
            html_content = self._serve_dev_dashboard()
            response = make_response(html_content)
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
            response.headers['ETag'] = f'"autopromptix-{int(time.time())}"'
            return response
        
        @self.app.route('/index.html')
        def index_html():
            """Serve the dashboard page"""
            return make_response(self._serve_dev_dashboard())
        
        @self.app.route('/dashboard/frontend/index.html')
        def frontend_index():
            """Serve the dashboard page"""
            return make_response(self._serve_dev_dashboard())
        
        @self.app.route('/src/<path:filename>')
        def vite_src_files(filename):
            """Block Vite source file requests"""
            return jsonify({'error': 'Vite development files not available'}), 404
        
        @self.app.route('/vite.svg')
        def vite_svg():
            """Block Vite SVG requests"""
            return jsonify({'error': 'Vite assets not available'}), 404
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            return jsonify({'error': 'Static files not available'}), 404
        
        @self.app.route('/assets/<path:filename>')
        def vite_assets(filename):
            """Serve assets"""
            return jsonify({'error': 'Assets not available'}), 404
        
        @self.app.route('/api/functions')
        def get_functions():
            """Get all registered functions"""
            registry = get_test_registry()
            functions = []
            
            for func_id, func_info in registry.items():
                metadata = func_info['metadata']
                stats = self.storage.get_function_stats(func_id)
                
                # Check if function has test data pool
                test_data_pool = self.test_data_manager.load_pool(func_id.split('.')[-1])
                
                functions.append({
                    'id': func_id,
                    'name': func_id.split('.')[-1],
                    'module': func_id.split('.')[0],
                    'metadata': metadata,
                    'stats': stats,
                    'has_test_pool': test_data_pool is not None,
                    'test_pool_info': {
                        'total_cases': test_data_pool.total_cases if test_data_pool else 0,
                        'description': test_data_pool.description if test_data_pool else ''
                    } if test_data_pool else None
                })
            
            return jsonify({
                'functions': functions,
                'total': len(functions)
            })
        
        @self.app.route('/api/test-pools')
        def get_test_pools():
            """Get all test data pools"""
            pools = self.test_data_manager.list_pools()
            pool_details = []
            
            for pool_name in pools:
                pool = self.test_data_manager.load_pool(pool_name)
                if pool:
                    stats = self.test_data_manager.get_statistics(pool_name)
                    pool_details.append({
                        'name': pool_name,
                        'description': pool.description,
                        'category': pool.category,
                        'stats': stats
                    })
            
            return jsonify({
                'pools': pool_details,
                'total': len(pools)
            })
        
        @self.app.route('/api/test-pools/<pool_name>')
        def get_pool_details(pool_name):
            """Get detailed information about a test data pool"""
            pool = self.test_data_manager.load_pool(pool_name)
            if not pool:
                return jsonify({'error': 'Test data pool not found'}), 404
            
            return jsonify({
                'name': pool_name,
                'description': pool.description,
                'category': pool.category,
                'test_cases': [
                    {
                        'id': case.id,
                        'input': case.input,
                        'expected_output': case.expected_output,
                        'description': case.description
                    } for case in pool.test_cases
                ]
            })
        
        @self.app.route('/api/test-pools', methods=['POST'])
        def create_pool():
            """Create a new test data pool"""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                pool_name = data.get('name')
                description = data.get('description', '')
                category = data.get('category', 'general')
                test_cases = data.get('test_cases', [])
                
                if not pool_name:
                    return jsonify({'error': 'Pool name is required'}), 400
                
                # Create test cases
                cases = []
                for case_data in test_cases:
                    case = TestCase(
                        id=case_data.get('id', f'case_{len(cases)}'),
                        input=case_data.get('input', ''),
                        expected_output=case_data.get('expected_output', ''),
                        description=case_data.get('description', '')
                    )
                    cases.append(case)
                
                # Create pool
                pool = TestDataPool(
                    name=pool_name,
                    description=description,
                    category=category,
                    test_cases=cases
                )
                
                self.test_data_manager.create_pool(pool)
                
                return jsonify({
                    'message': 'Test data pool created successfully',
                    'pool_name': pool_name
                }), 201
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/test-pools/<pool_name>', methods=['DELETE'])
        def delete_pool(pool_name):
            """Delete a test data pool"""
            try:
                success = self.test_data_manager.delete_pool(pool_name)
                if success:
                    return jsonify({
                        'message': 'Test data pool deleted successfully',
                        'pool_name': pool_name
                    })
                else:
                    return jsonify({'error': 'Test data pool not found'}), 404
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get overall system statistics"""
            registry = get_test_registry()
            total_functions = len(registry)
            
            pools = self.test_data_manager.list_pools()
            total_pools = len(pools)
            
            total_test_cases = 0
            for pool_name in pools:
                pool = self.test_data_manager.load_pool(pool_name)
                if pool:
                    total_test_cases += pool.total_cases
            
            return jsonify({
                'total_functions': total_functions,
                'total_test_pools': total_pools,
                'total_test_cases': total_test_cases,
                'system_status': 'running'
            })
    
    def _serve_dev_dashboard(self):
        """Serve a simple development dashboard"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>AutoPromptix Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .function-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .pool-item { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .stats { display: flex; gap: 20px; }
        .stat-box { background: #007bff; color: white; padding: 15px; border-radius: 4px; text-align: center; flex: 1; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .loading { text-align: center; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 AutoPromptix Dashboard</h1>
            <p>AI Function Testing and Improvement Framework</p>
        </div>
        
        <div class="card">
            <h2>📊 System Statistics</h2>
            <div id="stats" class="stats">
                <div class="loading">Loading statistics...</div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔧 Registered Functions</h2>
            <div id="functions">
                <div class="loading">Loading functions...</div>
            </div>
        </div>
        
        <div class="card">
            <h2>📦 Test Data Pools</h2>
            <div id="pools">
                <div class="loading">Loading test pools...</div>
            </div>
        </div>
    </div>

    <script>
        // Load statistics
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('stats').innerHTML = `
                    <div class="stat-box">
                        <h3>${data.total_functions}</h3>
                        <p>Functions</p>
                    </div>
                    <div class="stat-box">
                        <h3>${data.total_test_pools}</h3>
                        <p>Test Pools</p>
                    </div>
                    <div class="stat-box">
                        <h3>${data.total_test_cases}</h3>
                        <p>Test Cases</p>
                    </div>
                `;
            })
            .catch(error => {
                document.getElementById('stats').innerHTML = '<p>Error loading statistics</p>';
            });

        // Load functions
        fetch('/api/functions')
            .then(response => response.json())
            .then(data => {
                if (data.functions.length === 0) {
                    document.getElementById('functions').innerHTML = '<p>No functions registered</p>';
                } else {
                    const functionsHtml = data.functions.map(func => `
                        <div class="function-item">
                            <h3>${func.name}</h3>
                            <p><strong>Module:</strong> ${func.module}</p>
                            <p><strong>Description:</strong> ${func.metadata.description || 'No description'}</p>
                            <p><strong>Test Pool:</strong> ${func.has_test_pool ? 'Yes' : 'No'}</p>
                        </div>
                    `).join('');
                    document.getElementById('functions').innerHTML = functionsHtml;
                }
            })
            .catch(error => {
                document.getElementById('functions').innerHTML = '<p>Error loading functions</p>';
            });

        // Load test pools
        fetch('/api/test-pools')
            .then(response => response.json())
            .then(data => {
                if (data.pools.length === 0) {
                    document.getElementById('pools').innerHTML = '<p>No test pools found</p>';
                } else {
                    const poolsHtml = data.pools.map(pool => `
                        <div class="pool-item">
                            <h3>${pool.name}</h3>
                            <p><strong>Description:</strong> ${pool.description}</p>
                            <p><strong>Category:</strong> ${pool.category}</p>
                            <p><strong>Test Cases:</strong> ${pool.stats.total_cases || 0}</p>
                        </div>
                    `).join('');
                    document.getElementById('pools').innerHTML = poolsHtml;
                }
            })
            .catch(error => {
                document.getElementById('pools').innerHTML = '<p>Error loading test pools</p>';
            });
    </script>
</body>
</html>
        """
        return html
    
    def start(self):
        """Start the server"""
        if self.running:
            return
        
        self.running = True
        
        def run_server():
            self.app.run(host=self.host, port=self.port, debug=False)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"🚀 AutoPromptix Dashboard Server running on http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)


def create_app():
    """Create Flask app for WSGI deployment"""
    server = DashboardServer()
    return server.app


if __name__ == '__main__':
    server = DashboardServer()
    server.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Shutting down dashboard server...")
        server.stop() 