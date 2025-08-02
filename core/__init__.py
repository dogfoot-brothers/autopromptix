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
from .decorators import (
    test,
    test_config,
    prompt_template,
    test_context,
    auto_test,
    autopromptix
)
from .decorators import get_test_registry, get_function_metadata
from .storage import StorageManager
from .prompt_improver import PromptImprover
from .test_runner import TestRunner
from .test_data_pool import TestDataPoolManager, TestDataPool, TestCase

__version__ = "0.1.0"
__author__ = "AutoPromptix Team"

# Initialize storage and core components
storage = StorageManager()
prompt_improver = PromptImprover(storage)
test_runner = TestRunner(storage, prompt_improver)
test_data_manager = TestDataPoolManager()

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
    'autopromptix',
    # Core components
    'storage',
    'prompt_improver',
    'test_runner',
    'test_data_manager',
    # Functions
    'get_test_registry',
    'get_function_metadata',
    # Data models
    'TestDataPool',
    'TestCase'
] 