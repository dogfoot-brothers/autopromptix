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

# Initialize storage and core components
storage = StorageManager()
prompt_improver = PromptImprover(storage)
test_runner = TestRunner(storage, prompt_improver)

__all__ = [
    'selftest',
    'desiredoutput', 
    'self_test_system_prompt',
    'self_test_temperature',
    'self_test_k',
    'client',
    'start_server',
    'stop_server',
    'get_server',
    'storage',
    'prompt_improver',
    'test_runner'
] 