"""
AutoPromptix API Server

Unified API server providing both core functionality and AI-powered prompt optimization.
Combines Flask for REST endpoints with SocketIO for WebSocket support.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import sys
import os
import json
import uuid
from datetime import datetime
import asyncio
import logging
import traceback
from threading import Event

# Add core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core import (
    storage, prompt_improver, test_runner, test_data_manager,
    get_test_registry, get_function_metadata, TestDataPool
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active optimization sessions
optimization_sessions = {}

class APIServer:
    """Unified API server for AutoPromptix"""
    
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        
        # Initialize Flask app with SocketIO
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'autopromptix-secret-key'
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        
        # Initialize SocketIO with async mode
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            async_mode='eventlet',  # Use eventlet for better performance
            logger=True,
            engineio_logger=True
        )
        
        # Setup routes
        self._setup_routes()
        self._setup_socketio_handlers()
        
        # Server state
        self.running = False
        self.server_thread = None
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/')
        def root():
            """API root endpoint"""
            return jsonify({
                'message': 'AutoPromptix API Server',
                'version': '1.0.0',
                'features': [
                    'Automated Prompt Testing',
                    'AI-Powered Prompt Optimization',
                    'Test Data Pool Management',
                    'Real-time WebSocket Support'
                ],
                'endpoints': {
                    'core': ['/api/functions', '/api/test-pools', '/api/stats'],
                    'optimization': ['/api/prompt-optimization/optimize', '/api/prompt-optimization/examples'],
                    'websocket': 'Connect to /socket.io for real-time features'
                }
            })
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        
        # ============================================================================
        # CORE AUTOPROMPTIX ENDPOINTS
        # ============================================================================
        
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
            test_cases = data.get('test_cases', [])
            
            # Check if pool already exists
            existing_pool = test_data_manager.load_pool(pool_name)
            if existing_pool:
                return jsonify({'error': 'Test data pool already exists'}), 409
            
            # Create new pool
            new_pool = TestDataPool(
                name=pool_name,
                description=description,
                category=category
            )
            
            # Add test cases if provided
            for case_data in test_cases:
                new_pool.add_test_case(
                    input_data=case_data.get('input', ''),
                    expected_output=case_data.get('expected_output', ''),
                    description=case_data.get('description', '')
            )
            
            test_data_manager.create_pool(new_pool)
            
            return jsonify({
                'message': 'Test data pool created successfully',
                'pool': {
                    'name': pool_name,
                    'description': description,
                    'category': category,
                    'test_cases': len(test_cases)
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
                'total_test_cases': total_test_cases,
                'system_status': 'running'
            })
        
        # ============================================================================
        # PROMPT OPTIMIZATION ENDPOINTS
        # ============================================================================
        
        @self.app.route('/api/prompt-optimization/optimize', methods=['POST'])
        def optimize_prompt():
            """AI-powered prompt optimization endpoint"""
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Extract parameters
                user_input = data.get('user_input', '')
                expected_output = data.get('expected_output', '')
                product_name = data.get('product_name', '')
                exclude_keywords = data.get('exclude_keywords', [])
                custom_mutators = data.get('custom_mutators', [])
                evaluation_weights = data.get('evaluation_weights', {})
                
                if not user_input:
                    return jsonify({'error': 'user_input is required'}), 400
                
                # Set default expected output if empty
                if not expected_output:
                    expected_output = "Clear, specific, and practical response addressing the request"
                
                logger.info(f"Starting prompt optimization for: {user_input}")
                
                # Run optimization in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                from core.prompt_optimizer import optimize_prompt_simple
                
                result = loop.run_until_complete(
                    optimize_prompt_simple(
                        user_input=user_input,
                        expected_output=expected_output,
                        product_name=product_name,
                        exclude_keywords=exclude_keywords,
                        custom_mutators=custom_mutators,
                        evaluation_weights=evaluation_weights
                    )
                )
                
                logger.info(f"Optimization complete - Score: {result['best_score']}")
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Prompt optimization failed: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return jsonify({'error': f'Optimization error: {str(e)}'}), 500
        
        @self.app.route('/api/prompt-optimization/examples')
        def get_optimization_examples():
            """Get example optimization scenarios"""
            examples = [
                {
                    "title": "Customer Apology Email",
                    "description": "Transform vague request into specific, effective prompt",
                    "data": {
                        "user_input": "Write an apology email to customer",
                        "expected_output": "Professional apology email with reason, solution, and prevention measures",
                        "product_name": "CustomerService",
                        "exclude_keywords": ["never", "impossible", "cannot"],
                        "custom_mutators": [
                            "Use empathetic and professional tone",
                            "Include specific timeline and action items"
                        ]
                    }
                },
                {
                    "title": "Project Plan",
                    "description": "Convert simple request into detailed, actionable prompt",
                    "data": {
                        "user_input": "Create project plan",
                        "expected_output": "Comprehensive project plan with objectives, timeline, resources, and milestones",
                        "product_name": "ProjectManager",
                        "exclude_keywords": ["maybe", "perhaps", "might"],
                        "custom_mutators": [
                            "Include specific deliverables and deadlines",
                            "Add risk assessment and mitigation strategies"
                        ]
                    }
                },
                {
                    "title": "Technical Documentation",
                    "description": "Transform basic request into structured technical documentation",
                    "data": {
                        "user_input": "Write API documentation",
                        "expected_output": "Developer-friendly API docs with authentication, endpoints, and examples",
                        "product_name": "API",
                        "exclude_keywords": ["complex", "difficult"],
                        "custom_mutators": [
                            "Include step-by-step examples",
                            "Add error handling and best practices"
                        ]
                    }
                }
            ]
            
            return jsonify({"examples": examples})
        
        @self.app.route('/api/prompt-optimization/status')
        def get_optimization_status():
            """Check prompt optimization system status"""
            return jsonify({
                "status": "active",
                "version": "1.0.0",
                "features": [
                    "AI-powered prompt optimization",
                    "Smart mutation generation",
                    "Real-time streaming via WebSocket",
                    "Multi-metric evaluation",
                    "Custom requirements support"
                ],
                "endpoints": {
                    "optimize": "/api/prompt-optimization/optimize",
                    "examples": "/api/prompt-optimization/examples",
                    "streaming": "Connect via SocketIO for real-time optimization",
                    "status": "/api/prompt-optimization/status"
                }
            })
    
    def _setup_socketio_handlers(self):
        """Setup SocketIO WebSocket handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to AutoPromptix WebSocket'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info(f"Client disconnected: {request.sid}")
            # Clean up any active optimization sessions
            if request.sid in optimization_sessions:
                optimization_sessions[request.sid]['stop_event'].set()
                del optimization_sessions[request.sid]
        
        @self.socketio.on('start_optimization')
        def handle_optimization(data):
            """Handle optimization request via WebSocket"""
            session_id = request.sid
            logger.info(f"Starting optimization for session: {session_id}")
            
            # Create stop event for this session
            stop_event = Event()
            optimization_sessions[session_id] = {
                'stop_event': stop_event,
                'start_time': datetime.now()
            }
            
            # Extract parameters
            user_input = data.get('user_input', '')
            expected_output = data.get('expected_output', '')
            product_name = data.get('product_name', '')
            exclude_keywords = data.get('exclude_keywords', [])
            custom_mutators = data.get('custom_mutators', [])
            evaluation_weights = data.get('evaluation_weights', {})
            
            # Set default expected output if empty
            if not expected_output:
                expected_output = "Clear, specific, and practical response addressing the request"
            
            # Run optimization in a separate thread
            def run_optimization():
                try:
                    # Create event loop for this thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    from core.prompt_optimizer import optimize_prompt_streaming
                    
                    # Run the async generator
                    async def stream_optimization():
                        async for result in optimize_prompt_streaming(
                            user_input=user_input,
                            expected_output=expected_output,
                            product_name=product_name,
                            exclude_keywords=exclude_keywords,
                            custom_mutators=custom_mutators,
                            evaluation_weights=evaluation_weights,
                            stop_event=stop_event
                        ):
                            # Emit results to the specific client
                            self.socketio.emit(
                                'optimization_update',
                                {
                                    'type': result['type'],
                                    'data': result['data'],
                                    'timestamp': datetime.now().isoformat()
                                },
                                room=session_id
                            )
                            
                            # Small delay to prevent overwhelming the client
                            await asyncio.sleep(0.1)
                    
                    # Run the streaming optimization
                    loop.run_until_complete(stream_optimization())
                    
                    # Send completion message
                    self.socketio.emit(
                        'optimization_complete',
                        {
                            'message': 'Optimization completed successfully',
                            'timestamp': datetime.now().isoformat()
                        },
                        room=session_id
                    )
                    
                except Exception as e:
                    logger.error(f"Optimization error: {e}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    self.socketio.emit(
                        'optimization_error',
                        {
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        },
                        room=session_id
                    )
                finally:
                    # Clean up session
                    if session_id in optimization_sessions:
                        del optimization_sessions[session_id]
                    loop.close()
            
            # Start optimization in background thread
            import threading
            optimization_thread = threading.Thread(target=run_optimization)
            optimization_thread.daemon = True
            optimization_thread.start()
        
        @self.socketio.on('stop_optimization')
        def handle_stop_optimization():
            """Handle stop optimization request"""
            session_id = request.sid
            logger.info(f"Stopping optimization for session: {session_id}")
            
            if session_id in optimization_sessions:
                optimization_sessions[session_id]['stop_event'].set()
                emit('optimization_stopped', {
                    'message': 'Optimization stopped by user',
                    'timestamp': datetime.now().isoformat()
            })
    
    def start(self):
        """Start the API server"""
        if self.running:
            return
        
        self.running = True
        
        def run_server():
            # Run with SocketIO
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                log_output=True
            )
        
        import threading
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        print(f"AutoPromptix API Server running on http://{self.host}:{self.port}")
        print(f"WebSocket endpoint: ws://{self.host}:{self.port}/socket.io/")
    
    def stop(self):
        """Stop the API server"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=5) 


if __name__ == '__main__':
    # Direct execution for testing
    server = APIServer(host='0.0.0.0', port=8000)
    server.socketio.run(
        server.app,
        host='0.0.0.0',
        port=8000,
        debug=True
    )