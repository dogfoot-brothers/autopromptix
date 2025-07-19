"""
AutoPromptix - Automated Prompt Testing and Improvement Tool

A web-based server for testing and improving AI prompts automatically.
"""

from .decorators import (
    selftest,
    desiredoutput,
    self_test_system_prompt,
    self_test_temperature,
    self_test_k,
    client
)
from .enhanced_decorators import (
    test,
    test_config,
    prompt_template,
    test_context,
    auto_test
)
from .server import AutoPromptixServer
from .storage import StorageManager
from .prompt_improver import PromptImprover
from .test_runner import TestRunner

__version__ = "0.1.0"
__author__ = "AutoPromptix Team"

# Global server instance
_server = None

def start_server(host='127.0.0.1', port=8000, **kwargs):
    """Start the AutoPromptix web server"""
    global _server
    if _server is None:
        _server = AutoPromptixServer(host=host, port=port, **kwargs)
    return _server.start()

def stop_server():
    """Stop the AutoPromptix web server"""
    global _server
    if _server:
        _server.stop()
        _server = None

def get_server():
    """Get the current server instance"""
    return _server

def quick_start(port=8000, **kwargs):
    """Quick start AutoPromptix server"""
    return start_server(port=port, **kwargs)

def start_from_config(config_path: str):
    """Start AutoPromptix from configuration file"""
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    return start_server(**config.get('server', {}))

# Initialize storage and core components
storage = StorageManager()
prompt_improver = PromptImprover(storage)
test_runner = TestRunner(storage, prompt_improver)

__all__ = [
    # Legacy decorators
    'selftest',
    'desiredoutput', 
    'self_test_system_prompt',
    'self_test_temperature',
    'self_test_k',
    'client',
    # Enhanced decorators
    'test',
    'test_config',
    'prompt_template',
    'test_context',
    'auto_test',
    # Server functions
    'start_server',
    'stop_server',
    'get_server',
    'quick_start',
    'start_from_config',
    # Core components
    'storage',
    'prompt_improver',
    'test_runner'
] 