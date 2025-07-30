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
# Server functionality moved to dashboard/backend/server.py
# from .server import AutoPromptixServer
from .storage import StorageManager
from .prompt_improver import PromptImprover
from .test_runner import TestRunner

__version__ = "0.1.0"
__author__ = "AutoPromptix Team"

# Global server instance
_server = None

def start_server(host='127.0.0.1', port=8000, **kwargs):
    """Start the AutoPromptix web server (deprecated - use enhanced_main.py)"""
    print("Warning: start_server is deprecated. Use enhanced_main.py instead.")
    return None

def stop_server():
    """Stop the AutoPromptix web server (deprecated)"""
    print("Warning: stop_server is deprecated. Use enhanced_main.py instead.")
    return None

def get_server():
    """Get the current server instance (deprecated)"""
    print("Warning: get_server is deprecated. Use enhanced_main.py instead.")
    return None

def quick_start(port=8000, **kwargs):
    """Quick start AutoPromptix server (deprecated)"""
    print("Warning: quick_start is deprecated. Use enhanced_main.py instead.")
    return None

def start_from_config(config_path: str):
    """Start AutoPromptix from configuration file (deprecated)"""
    print("Warning: start_from_config is deprecated. Use enhanced_main.py instead.")
    return None

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
    # Core components
    'storage',
    'prompt_improver',
    'test_runner'
] 