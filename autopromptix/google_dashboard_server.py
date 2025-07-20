"""
Google-Style AutoPromptix Dashboard Server

Modern Material Design-inspired dashboard with Test Data Pool management.
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import threading
import time
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .storage import StorageManager
from .prompt_improver import PromptImprover
from .test_runner import TestRunner, TestResult
from .enhanced_decorators import get_test_registry, get_function_metadata
from .test_data_pool import TestDataPoolManager, TestDataPool, TestCase

class GoogleStyleDashboardServer:
    """Google Material Design-inspired dashboard server with Test Data Pool management"""
    
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
            """Main dashboard page with Test Data Pool management"""
            return render_template_string(DASHBOARD_TEMPLATE)
        
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
        
        print(f"🚀 Google Style Dashboard Server running on http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)


# Dashboard Template with Test Data Pool Management
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoPromptix - Test Data Pool Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body { 
            font-family: 'Roboto', sans-serif;
            background: #f5f5f5;
            color: #202124;
            line-height: 1.6;
        }
        
        .app-bar {
            background: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 0 24px;
            height: 64px;
            display: flex;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .app-title {
            font-size: 22px;
            font-weight: 500;
            color: #1a73e8;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 24px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .stat-card {
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            transition: box-shadow 0.2s ease;
        }
        
        .stat-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .stat-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .stat-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 20px;
        }
        
        .stat-icon.blue { background: #1a73e8; }
        .stat-icon.green { background: #34a853; }
        .stat-icon.orange { background: #fbbc04; }
        .stat-icon.purple { background: #9c27b0; }
        
        .stat-title {
            font-size: 14px;
            color: #5f6368;
            font-weight: 500;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 400;
            color: #202124;
            margin-bottom: 8px;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
        }
        
        .main-content {
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        .sidebar {
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        .section-title {
            font-size: 20px;
            font-weight: 500;
            color: #202124;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .tabs {
            display: flex;
            border-bottom: 1px solid #e8eaed;
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 12px 24px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            color: #5f6368;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .tab.active {
            color: #1a73e8;
            border-bottom-color: #1a73e8;
        }
        
        .tab:hover {
            color: #1a73e8;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .function-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .function-item {
            border: 1px solid #e8eaed;
            border-radius: 8px;
            padding: 16px;
            transition: all 0.2s ease;
            position: relative;
            cursor: pointer;
        }
        
        .function-item:hover {
            border-color: #1a73e8;
            box-shadow: 0 4px 12px rgba(26, 115, 232, 0.15);
            transform: translateY(-2px);
        }
        
        .function-tooltip {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #202124;
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            margin-top: 8px;
        }
        
        .function-item:hover .function-tooltip {
            opacity: 1;
            visibility: visible;
        }
        
        .function-tooltip::before {
            content: '';
            position: absolute;
            top: -6px;
            left: 20px;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-bottom: 6px solid #202124;
        }
        
        .tooltip-section {
            margin-bottom: 8px;
        }
        
        .tooltip-section:last-child {
            margin-bottom: 0;
        }
        
        .tooltip-title {
            font-weight: 600;
            color: #8ab4f8;
            margin-bottom: 4px;
        }
        
        .tooltip-content {
            color: #e8eaed;
            line-height: 1.4;
        }
        
        .function-name {
            font-weight: 500;
            color: #202124;
            margin-bottom: 8px;
            font-size: 16px;
        }
        
        .function-meta {
            font-size: 12px;
            color: #5f6368;
            margin-bottom: 12px;
        }
        
        .function-stats {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        
        .stat-badge {
            background: #f1f3f4;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 12px;
            color: #5f6368;
            font-weight: 500;
        }
        
        .test-pool-badge {
            background: #e8f0fe;
            color: #1a73e8;
            padding: 6px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .action-buttons {
            display: flex;
            gap: 8px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }
        
        .btn-primary {
            background: #1a73e8;
            color: #fff;
        }
        
        .btn-primary:hover {
            background: #1557b0;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(26, 115, 232, 0.3);
        }
        
        .btn-secondary {
            background: #f1f3f4;
            color: #5f6368;
        }
        
        .btn-secondary:hover {
            background: #e8eaed;
            transform: translateY(-1px);
        }
        
        .btn-success {
            background: #34a853;
            color: #fff;
        }
        
        .btn-success:hover {
            background: #2d8a47;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(52, 168, 83, 0.3);
        }
        
        .btn-warning {
            background: #fbbc04;
            color: #fff;
        }
        
        .btn-warning:hover {
            background: #f9ab00;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(251, 188, 4, 0.3);
        }
        
        .test-pool-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            transition: all 0.2s ease;
            border: 1px solid #e8eaed;
        }
        
        .test-pool-card:hover {
            border-color: #1a73e8;
            box-shadow: 0 2px 8px rgba(26, 115, 232, 0.1);
            transform: translateY(-1px);
        }
        
        .test-pool-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .test-pool-title {
            font-weight: 500;
            color: #202124;
            font-size: 16px;
        }
        
        .test-pool-stats {
            display: flex;
            gap: 8px;
            font-size: 12px;
            color: #5f6368;
        }
        
        .test-pool-stat {
            background: #fff;
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid #e8eaed;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #5f6368;
        }
        
        .empty-state-icon {
            font-size: 48px;
            color: #dadce0;
            margin-bottom: 16px;
        }
        
        .empty-state-title {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 8px;
            color: #202124;
        }
        
        .empty-state-description {
            font-size: 14px;
            line-height: 1.5;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: #fff;
            margin: 5% auto;
            padding: 24px;
            border-radius: 12px;
            width: 80%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-title {
            font-size: 20px;
            font-weight: 500;
            color: #202124;
        }
        
        .close {
            color: #5f6368;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #202124;
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #202124;
        }
        
        .form-input {
            width: 100%;
            padding: 12px;
            border: 1px solid #e8eaed;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s ease;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #1a73e8;
        }
        
        .form-textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #e8eaed;
            border-radius: 6px;
            font-size: 14px;
            font-family: monospace;
            resize: vertical;
            min-height: 100px;
            transition: border-color 0.2s ease;
        }
        
        .form-textarea:focus {
            outline: none;
            border-color: #1a73e8;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #5f6368;
        }
        
        .error {
            background: #fce8e6;
            color: #d93025;
            padding: 12px;
            border-radius: 8px;
            margin: 16px 0;
        }
        
        .success {
            background: #e6f4ea;
            color: #137333;
            padding: 12px;
            border-radius: 8px;
            margin: 16px 0;
        }
        
        @media (max-width: 768px) {
            .content-grid {
                grid-template-columns: 1fr;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .modal-content {
                width: 95%;
                margin: 10% auto;
            }
        }
    </style>
</head>
<body>
    <div class="app-bar">
        <div class="app-title">
            <span class="material-icons">auto_awesome</span>
            AutoPromptix Test Data Pool Dashboard
        </div>
    </div>
    
    <div class="main-container">
        <div class="stats-grid" id="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon blue">
                        <span class="material-icons">functions</span>
                    </div>
                    <div>
                        <div class="stat-title">Functions</div>
                        <div class="stat-value" id="total-functions">0</div>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon green">
                        <span class="material-icons">data_object</span>
                    </div>
                    <div>
                        <div class="stat-title">Test Pools</div>
                        <div class="stat-value" id="total-pools">0</div>
                    </div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <div class="stat-icon orange">
                        <span class="stat-icon orange">
                            <span class="material-icons">science</span>
                        </div>
                    </div>
                    <div>
                        <div class="stat-title">Test Cases</div>
                        <div class="stat-value" id="total-test-cases">0</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="main-content">
                <div class="section-title">
                    <span class="material-icons">dashboard</span>
                    AutoPromptix Dashboard
                </div>
                
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('functions')">
                        <span class="material-icons">functions</span>
                        Functions
                    </div>
                    <div class="tab" onclick="switchTab('test-pools')">
                        <span class="material-icons">data_object</span>
                        Test Data Pools
                    </div>
                </div>
                
                <div id="functions-tab" class="tab-content active">
                    <div id="functions-container" class="loading">
                        Loading functions...
                    </div>
                </div>
                
                <div id="test-pools-tab" class="tab-content">
                    <div id="test-pools-container" class="loading">
                        Loading test data pools...
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="section-title">
                    <span class="material-icons">dashboard</span>
                    Quick Actions
                </div>
                
                <div class="action-buttons" style="flex-direction: column; gap: 12px;">
                    <button class="btn btn-primary" onclick="createTestPool()">
                        <span class="material-icons">add</span>
                        Create Test Pool
                    </button>
                    <button class="btn btn-secondary" onclick="refreshData()">
                        <span class="material-icons">refresh</span>
                        Refresh Data
                    </button>
                </div>
                
                <div style="margin-top: 24px;">
                    <div class="section-title">
                        <span class="material-icons">info</span>
                        System Info
                    </div>
                    <div id="system-info">
                        <div class="stat-badge">Server: Running</div>
                        <div class="stat-badge">Port: 8001</div>
                        <div class="stat-badge">Version: 1.0</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Test Pool Modal -->
    <div id="testPoolModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="modalTitle">Create Test Data Pool</div>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <form id="testPoolForm">
                <div class="form-group">
                    <label class="form-label">Function Name</label>
                    <input type="text" class="form-input" id="poolFunctionName" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" id="poolDescription">
                </div>
                <div class="form-group">
                    <label class="form-label">Category</label>
                    <input type="text" class="form-input" id="poolCategory" value="general">
                </div>
                <div class="form-group">
                    <label class="form-label">Test Cases (JSON)</label>
                    <textarea class="form-textarea" id="poolTestCases" placeholder='[{"id": "test_001", "input": "Hello", "expected_output": "Hi!", "weight": 1.0, "tags": ["basic"]}]'></textarea>
                </div>
                <div class="action-buttons">
                    <button type="submit" class="btn btn-primary">Create Pool</button>
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        let currentTab = 'functions';
        
        // Tab switching
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName + '-tab').classList.add('active');
            
            currentTab = tabName;
            
            if (tabName === 'functions') {
                loadFunctions();
            } else if (tabName === 'test-pools') {
                loadTestPools();
            }
        }
        
        // Load dashboard data
        async function loadDashboard() {
            try {
                const [statsResponse, functionsResponse, poolsResponse] = await Promise.all([
                    fetch('/api/stats'),
                    fetch('/api/functions'),
                    fetch('/api/test-pools')
                ]);
                
                const stats = await statsResponse.json();
                const functions = await functionsResponse.json();
                const pools = await poolsResponse.json();
                
                updateStats(stats, pools);
                
                if (currentTab === 'functions') {
                    updateFunctions(functions.functions);
                } else if (currentTab === 'test-pools') {
                    updateTestPools(pools.pools);
                }
            } catch (error) {
                console.error('Error loading dashboard:', error);
                document.getElementById('functions-container').innerHTML = 
                    '<div class="error">Error loading dashboard data</div>';
            }
        }
        
        function updateStats(stats, pools) {
            document.getElementById('total-functions').textContent = stats.total_functions;
            document.getElementById('total-pools').textContent = stats.total_test_pools;
            document.getElementById('total-test-cases').textContent = stats.total_test_cases;
        }
        
        async function loadFunctions() {
            try {
                const response = await fetch('/api/functions');
                const data = await response.json();
                updateFunctions(data.functions);
            } catch (error) {
                console.error('Error loading functions:', error);
            }
        }
        
        function updateFunctions(functions) {
            const container = document.getElementById('functions-container');
            
            if (functions.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📝</div>
                        <div class="empty-state-title">No Functions Found</div>
                        <div class="empty-state-description">
                            Add @autopromptix decorators to your functions to see them here.
                        </div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = '<div class="function-list">' + 
                functions.map(func => `
                    <div class="function-item" onmouseenter="showTooltip(this, '${func.id}')" onmouseleave="hideTooltip(this)">
                        <div class="function-name">${func.name}()</div>
                        <div class="function-meta">${func.module}</div>
                        <div class="function-stats">
                            <div class="stat-badge">Role: ${func.metadata.role}</div>
                            <div class="stat-badge">Temp: ${func.metadata.temperature}</div>
                            <div class="stat-badge">Max: ${func.metadata.max_tokens}</div>
                            ${func.has_test_pool ? `<div class="test-pool-badge">📦 Test Pool: ${func.test_pool_info.total_cases} cases</div>` : ''}
                        </div>
                        <div class="action-buttons">
                            <button class="btn btn-primary" onclick="runTest('${func.id}')">
                                <span class="material-icons">play_arrow</span>
                                Test
                            </button>
                            ${func.has_test_pool ? `<button class="btn btn-warning" onclick="viewTestPool('${func.name}')">
                                <span class="material-icons">data_object</span>
                                View Pool
                            </button>` : ''}
                        </div>
                        <div class="function-tooltip" id="tooltip-${func.id}">
                            <div class="tooltip-section">
                                <div class="tooltip-title">Function Details</div>
                                <div class="tooltip-content">
                                    <strong>Name:</strong> ${func.name}<br>
                                    <strong>Module:</strong> ${func.module}<br>
                                    <strong>Role:</strong> ${func.metadata.role}<br>
                                    <strong>Temperature:</strong> ${func.metadata.temperature}<br>
                                    <strong>Max Tokens:</strong> ${func.metadata.max_tokens}
                                </div>
                            </div>
                            ${func.has_test_pool ? `
                            <div class="tooltip-section">
                                <div class="tooltip-title">Test Data Pool</div>
                                <div class="tooltip-content">
                                    <strong>Pool:</strong> ${func.name}_test_cases<br>
                                    <strong>Total Cases:</strong> ${func.test_pool_info.total_cases}<br>
                                    <strong>Description:</strong> ${func.test_pool_info.description || 'No description'}
                                </div>
                            </div>
                            ` : `
                            <div class="tooltip-section">
                                <div class="tooltip-title">No Test Pool</div>
                                <div class="tooltip-content">
                                    This function doesn't have a test data pool yet.<br>
                                    Create one to enable comprehensive testing.
                                </div>
                            </div>
                            `}
                            <div class="tooltip-section">
                                <div class="tooltip-title">Quick Actions</div>
                                <div class="tooltip-content">
                                    • Click "Test" to run a quick test<br>
                                    • Click "View Pool" to see test cases<br>
                                    • Hover over other functions for details
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('') +
                '</div>';
        }
        
        function showTooltip(element, funcId) {
            const tooltip = element.querySelector('.function-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '1';
                tooltip.style.visibility = 'visible';
            }
        }
        
        function hideTooltip(element) {
            const tooltip = element.querySelector('.function-tooltip');
            if (tooltip) {
                tooltip.style.opacity = '0';
                tooltip.style.visibility = 'hidden';
            }
        }
        
        async function loadTestPools() {
            try {
                const response = await fetch('/api/test-pools');
                const data = await response.json();
                updateTestPools(data.pools);
            } catch (error) {
                console.error('Error loading test pools:', error);
            }
        }
        
        function updateTestPools(pools) {
            const container = document.getElementById('test-pools-container');
            
            if (pools.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📦</div>
                        <div class="empty-state-title">No Test Data Pools</div>
                        <div class="empty-state-description">
                            Create your first test data pool to get started with comprehensive testing.
                        </div>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = pools.map(pool => `
                <div class="test-pool-card">
                    <div class="test-pool-header">
                        <div class="test-pool-title">${pool.name}</div>
                        <div class="test-pool-stats">
                            <div class="test-pool-stat">${pool.stats.total_cases} total</div>
                            <div class="test-pool-stat">${pool.stats.test_cases} test</div>
                            <div class="test-pool-stat">${pool.stats.edge_cases} edge</div>
                            <div class="test-pool-stat">${pool.stats.negative_cases} negative</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 12px; color: #5f6368; font-size: 14px;">
                        ${pool.description}
                    </div>
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="viewTestPool('${pool.name}')">
                            <span class="material-icons">visibility</span>
                            View Details
                        </button>
                        <button class="btn btn-warning" onclick="deleteTestPool('${pool.name}')">
                            <span class="material-icons">delete</span>
                            Delete
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        function createTestPool() {
            document.getElementById('modalTitle').textContent = 'Create Test Data Pool';
            document.getElementById('testPoolForm').reset();
            document.getElementById('testPoolModal').style.display = 'block';
        }
        
        function closeModal() {
            document.getElementById('testPoolModal').style.display = 'none';
        }
        
        document.getElementById('testPoolForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            try {
                const formData = {
                    function_name: document.getElementById('poolFunctionName').value,
                    description: document.getElementById('poolDescription').value,
                    category: document.getElementById('poolCategory').value,
                    test_cases: JSON.parse(document.getElementById('poolTestCases').value || '[]')
                };
                
                const response = await fetch('/api/test-pools', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Test data pool created successfully!');
                    closeModal();
                    loadDashboard();
                } else {
                    alert(`Failed to create pool: ${result.error}`);
                }
            } catch (error) {
                alert(`Error creating pool: ${error.message}`);
            }
        });
        
        async function deleteTestPool(poolName) {
            if (!confirm(`Are you sure you want to delete the test pool "${poolName}"?`)) {
                return;
            }
            
            try {
                const response = await fetch(`/api/test-pools/${poolName}`, {
                    method: 'DELETE'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Test data pool deleted successfully!');
                    loadDashboard();
                } else {
                    alert(`Failed to delete pool: ${result.error}`);
                }
            } catch (error) {
                alert(`Error deleting pool: ${error.message}`);
            }
        }
        
        async function viewTestPool(poolName) {
            try {
                const response = await fetch(`/api/test-pools/${poolName}`);
                const pool = await response.json();
                
                let casesHtml = '';
                if (pool.test_cases.length > 0) {
                    casesHtml += '<h4>Test Cases:</h4>';
                    pool.test_cases.forEach(case_ => {
                        casesHtml += `
                            <div style="background: white; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 3px solid #1a73e8;">
                                <div style="font-weight: 500; color: #1a73e8; margin-bottom: 8px;">${case_.id}</div>
                                <div style="font-size: 13px; color: #5f6368;">
                                    <div style="background: #f1f3f4; padding: 8px; border-radius: 4px; margin-bottom: 4px;">
                                        <strong>Input:</strong> ${case_.input}
                                    </div>
                                    <div style="background: #e8f5e8; padding: 8px; border-radius: 4px;">
                                        <strong>Expected:</strong> ${case_.expected_output}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                }
                
                const modal = document.createElement('div');
                modal.className = 'modal';
                modal.style.display = 'block';
                modal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <div class="modal-title">Test Pool: ${pool.name}</div>
                            <span class="close" onclick="this.parentElement.parentElement.parentElement.remove()">&times;</span>
                        </div>
                        <div>
                            <p><strong>Description:</strong> ${pool.description}</p>
                            <p><strong>Category:</strong> ${pool.category}</p>
                            <p><strong>Total Cases:</strong> ${pool.test_cases.length + pool.edge_cases.length + pool.negative_cases.length}</p>
                            ${casesHtml}
                        </div>
                    </div>
                `;
                document.body.appendChild(modal);
                
            } catch (error) {
                alert(`Error loading test pool: ${error.message}`);
            }
        }
        
        function refreshData() {
            loadDashboard();
        }
        
        // Load dashboard on page load
        loadDashboard();
        
        // Refresh every 30 seconds
        setInterval(loadDashboard, 30000);
    </script>
</body>
</html>
""" 