"""
AutoPromptix Dashboard Backend Server

Flask server for AutoPromptix dashboard that connects to API layer.
"""

from flask import Flask, request, jsonify, send_from_directory, send_file, make_response
from flask_cors import CORS
import json
import threading
import time
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

class DashboardServer:
    """Dashboard backend server for AutoPromptix"""
    
    def __init__(self, host='127.0.0.1', port=8001, api_url='http://localhost:8000'):
        self.host = host
        self.port = port
        self.api_url = api_url
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Setup routes
        self._setup_routes()
        
        # Server state
        self.running = False
        self.server_thread = None
    
    def _call_api(self, endpoint: str, method='GET', data=None):
        """Call API server"""
        url = f"{self.api_url}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                return None
            
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None
    
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
            """Get all registered functions from API"""
            result = self._call_api('/api/functions')
            if result:
                return jsonify(result)
            else:
                return jsonify({'error': 'API server not available'}), 503
        
        @self.app.route('/api/test-pools')
        def get_test_pools():
            """Get all test data pools from API"""
            result = self._call_api('/api/test-pools')
            if result:
                return jsonify(result)
            else:
                return jsonify({'error': 'API server not available'}), 503
        
        @self.app.route('/api/test-pools/<pool_name>')
        def get_pool_details(pool_name):
            """Get detailed information about a test data pool from API"""
            result = self._call_api(f'/api/test-pools/{pool_name}')
            if result:
                return jsonify(result)
            else:
                return jsonify({'error': 'API server not available'}), 503
        
        @self.app.route('/api/test-pools', methods=['POST'])
        def create_pool():
            """Create a new test data pool via API"""
            data = request.get_json()
            result = self._call_api('/api/test-pools', method='POST', data=data)
            if result:
                return jsonify(result), 201
            else:
                return jsonify({'error': 'API server not available'}), 503
        
        @self.app.route('/api/test-pools/<pool_name>', methods=['DELETE'])
        def delete_pool(pool_name):
            """Delete a test data pool via API"""
            result = self._call_api(f'/api/test-pools/{pool_name}', method='DELETE')
            if result:
                return jsonify(result)
            else:
                return jsonify({'error': 'API server not available'}), 503
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get overall system statistics from API"""
            result = self._call_api('/api/stats')
            if result:
                return jsonify(result)
            else:
                return jsonify({'error': 'API server not available'}), 503
    
    
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
        
        print(f"AutoPromptix Dashboard API Server running on http://{self.host}:{self.port}")
        print(f"Frontend should be served separately on port 3000")
        print(f"API endpoints available at http://{self.host}:{self.port}/api/*")
    
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
