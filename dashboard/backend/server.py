"""
AutoPromptix Dashboard Backend Server

Flask API server for AutoPromptix dashboard with Test Data Pool management.
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
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
from autopromptix.enhanced_decorators import get_test_registry, get_function_metadata
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
        
        # Get frontend directory path
        frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        frontend_dir = os.path.abspath(frontend_dir)
        
        @self.app.route('/')
        def index():
            """Serve the main dashboard page"""
            # Check if built files exist (production)
            dist_dir = os.path.join(frontend_dir, 'dist')
            if os.path.exists(os.path.join(dist_dir, 'index.html')):
                return send_file(os.path.join(dist_dir, 'index.html'))
            # Development fallback
            return send_file(os.path.join(frontend_dir, 'index.html'))
        
        @self.app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            # Check if built files exist (production)
            dist_dir = os.path.join(frontend_dir, 'dist')
            if os.path.exists(dist_dir):
                return send_from_directory(dist_dir, filename)
            # Development fallback
            return send_from_directory(frontend_dir, filename)
        
        @self.app.route('/assets/<path:filename>')
        def vite_assets(filename):
            """Serve Vite built assets"""
            dist_dir = os.path.join(frontend_dir, 'dist', 'assets')
            return send_from_directory(dist_dir, filename)
        
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
                        'weight': case.weight,
                        'tags': case.tags,
                        'description': case.description
                    }
                    for case in pool.test_cases
                ],
                'edge_cases': [
                    {
                        'id': case.id,
                        'input': case.input,
                        'expected_output': case.expected_output,
                        'weight': case.weight,
                        'tags': case.tags,
                        'description': case.description
                    }
                    for case in pool.edge_cases
                ],
                'negative_cases': [
                    {
                        'id': case.id,
                        'input': case.input,
                        'expected_output': case.expected_output,
                        'weight': case.weight,
                        'tags': case.tags,
                        'description': case.description
                    }
                    for case in pool.negative_cases
                ]
            })
        
        @self.app.route('/api/test-pools', methods=['POST'])
        def create_pool():
            """Create a new test data pool"""
            data = request.get_json() or {}
            
            try:
                # Create test cases
                test_cases = []
                for case_data in data.get('test_cases', []):
                    test_cases.append(TestCase(
                        id=case_data['id'],
                        input=case_data['input'],
                        expected_output=case_data['expected_output'],
                        weight=case_data.get('weight', 1.0),
                        tags=case_data.get('tags', []),
                        description=case_data.get('description', '')
                    ))
                
                # Create pool
                pool = TestDataPool(
                    function_name=data['function_name'],
                    description=data.get('description', ''),
                    category=data.get('category', 'general'),
                    test_cases=test_cases,
                    edge_cases=[],
                    negative_cases=[]
                )
                
                success = self.test_data_manager.create_pool(pool)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Test data pool "{data["function_name"]}" created successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to create test data pool'
                    }), 500
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
        
        @self.app.route('/api/test-pools/<pool_name>', methods=['DELETE'])
        def delete_pool(pool_name):
            """Delete a test data pool"""
            try:
                success = self.test_data_manager.delete_pool(pool_name)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Test data pool "{pool_name}" deleted successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to delete test data pool'
                    }), 500
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get overall statistics"""
            registry = get_test_registry()
            total_functions = len(registry)
            
            # Get test data pool stats
            test_pools = self.test_data_manager.list_pools()
            total_test_cases = 0
            for pool_name in test_pools:
                stats = self.test_data_manager.get_statistics(pool_name)
                total_test_cases += stats.get('total_cases', 0)
            
            return jsonify({
                'total_functions': total_functions,
                'total_test_pools': len(test_pools),
                'total_test_cases': total_test_cases
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