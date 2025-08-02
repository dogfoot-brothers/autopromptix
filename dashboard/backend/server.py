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
        
        @self.app.route('/')
        def index():
            """API root endpoint"""
            return jsonify({
                'message': 'AutoPromptix Dashboard API',
                'version': '1.0.0',
                'status': 'running',
                'endpoints': [
                    '/api/stats',
                    '/api/functions',
                    '/api/test-pools',
                    '/api/test-pools/<pool_name>',
                ]
            })
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        
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
        
        print(f"🚀 AutoPromptix Dashboard API Server running on http://{self.host}:{self.port}")
        print(f"📱 Frontend should be served separately on port 3000")
        print(f"🔗 API endpoints available at http://{self.host}:{self.port}/api/*")
    
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