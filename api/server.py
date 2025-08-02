"""
AutoPromptix API Server

REST API server that provides access to core functionality.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core import (
    storage, prompt_improver, test_runner, test_data_manager,
    get_test_registry, get_function_metadata
)

class APIServer:
    """API server for AutoPromptix core functionality"""
    
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Setup routes
        self._setup_routes()
        
        # Server state
        self.running = False
        self.server_thread = None
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/functions')
        def get_functions():
            """Get all registered functions"""
            registry = get_test_registry()
            functions = []
            
            for func_id, func_info in registry.items():
                metadata = func_info['metadata']
                stats = storage.get_function_stats(func_id)
                
                # Check if function has test data pool
                test_data_pool = test_data_manager.load_pool(func_id.split('.')[-1])
                
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
            pools = test_data_manager.list_pools()
            pool_details = []
            
            for pool_name in pools:
                pool = test_data_manager.load_pool(pool_name)
                if pool:
                    stats = test_data_manager.get_statistics(pool_name)
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
            pool = test_data_manager.load_pool(pool_name)
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
            data = request.get_json()
            
            if not data or 'name' not in data:
                return jsonify({'error': 'Pool name is required'}), 400
            
            pool_name = data['name']
            description = data.get('description', '')
            category = data.get('category', 'general')
            
            # Check if pool already exists
            existing_pool = test_data_manager.load_pool(pool_name)
            if existing_pool:
                return jsonify({'error': 'Test data pool already exists'}), 409
            
            # Create new pool
            from core import TestDataPool
            new_pool = TestDataPool(
                name=pool_name,
                description=description,
                category=category
            )
            
            test_data_manager.create_pool(new_pool)
            
            return jsonify({
                'message': 'Test data pool created successfully',
                'pool': {
                    'name': pool_name,
                    'description': description,
                    'category': category
                }
            }), 201
        
        @self.app.route('/api/test-pools/<pool_name>', methods=['DELETE'])
        def delete_pool(pool_name):
            """Delete a test data pool"""
            pool = test_data_manager.load_pool(pool_name)
            if not pool:
                return jsonify({'error': 'Test data pool not found'}), 404
            
            test_data_manager.delete_pool(pool_name)
            
            return jsonify({
                'message': 'Test data pool deleted successfully'
            })
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get overall system statistics"""
            registry = get_test_registry()
            
            total_functions = len(registry)
            total_pools = len(test_data_manager.list_pools())
            
            # Calculate total test cases
            total_test_cases = 0
            for pool_name in test_data_manager.list_pools():
                pool = test_data_manager.load_pool(pool_name)
                if pool:
                    total_test_cases += pool.total_cases
            
            return jsonify({
                'total_functions': total_functions,
                'total_pools': total_pools,
                'total_test_cases': total_test_cases
            })
    
    def start(self):
        """Start the API server"""
        if self.running:
            return
        
        self.running = True
        
        def run_server():
            self.app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False
            )
        
        import threading
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def stop(self):
        """Stop the API server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=5) 