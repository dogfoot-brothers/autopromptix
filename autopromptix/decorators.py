"""
AutoPromptix Decorators

Decorators for marking functions for automated prompt testing and improvement.
"""

import functools
import inspect
import json
import os
from typing import Callable, Any, Dict, List, Optional
from .storage import StorageManager

# Global registry for decorated functions
_test_registry = {}

def _get_storage():
    """Get the storage manager instance"""
    from . import storage
    return storage

def selftest(func: Callable) -> Callable:
    """
    Decorator to mark a function for self-testing
    
    This will automatically test the function with various prompts
    and collect performance metrics.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Register the function for testing
        func_id = f"{func.__module__}.{func.__name__}"
        if func_id not in _test_registry:
            _test_registry[func_id] = {
                'function': func,
                'metadata': {},
                'test_results': []
            }
        
        # Execute the original function
        result = func(*args, **kwargs)
        
        # Store the execution result
        storage = _get_storage()
        storage.log_execution(func_id, args, kwargs, result)
        
        return result
    
    wrapper._autopromptix_selftest = True
    return wrapper

def desiredoutput(output_path: str) -> Callable:
    """
    Decorator to specify the desired output for testing
    
    Args:
        output_path: Path to file containing expected output,
                    can include line references like '/output.txt/@L31'
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Parse the output path
            file_path = output_path
            line_ref = None
            
            if '@L' in output_path:
                file_path, line_ref = output_path.split('@L')
                line_ref = int(line_ref)
            
            # Get function ID
            func_id = f"{func.__module__}.{func.__name__}"
            
            # Store desired output information
            if func_id not in _test_registry:
                _test_registry[func_id] = {
                    'function': func,
                    'metadata': {},
                    'test_results': []
                }
            
            _test_registry[func_id]['metadata']['desired_output'] = {
                'file_path': file_path,
                'line_ref': line_ref
            }
            
            return func(*args, **kwargs)
        
        wrapper._autopromptix_desiredoutput = output_path
        return wrapper
    
    return decorator

def self_test_system_prompt(func: Callable) -> Callable:
    """
    Decorator to enable system prompt testing
    
    This will test the function with different system prompts
    to find the optimal prompt configuration.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_id = f"{func.__module__}.{func.__name__}"
        
        if func_id not in _test_registry:
            _test_registry[func_id] = {
                'function': func,
                'metadata': {},
                'test_results': []
            }
        
        _test_registry[func_id]['metadata']['test_system_prompt'] = True
        
        return func(*args, **kwargs)
    
    wrapper._autopromptix_system_prompt = True
    return wrapper

def self_test_temperature(func: Callable) -> Callable:
    """
    Decorator to enable temperature testing
    
    This will test the function with different temperature values
    to find the optimal setting.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_id = f"{func.__module__}.{func.__name__}"
        
        if func_id not in _test_registry:
            _test_registry[func_id] = {
                'function': func,
                'metadata': {},
                'test_results': []
            }
        
        _test_registry[func_id]['metadata']['test_temperature'] = True
        
        return func(*args, **kwargs)
    
    wrapper._autopromptix_temperature = True
    return wrapper

def self_test_k(func: Callable) -> Callable:
    """
    Decorator to enable top-k testing
    
    This will test the function with different top-k values
    to find the optimal setting.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_id = f"{func.__module__}.{func.__name__}"
        
        if func_id not in _test_registry:
            _test_registry[func_id] = {
                'function': func,
                'metadata': {},
                'test_results': []
            }
        
        _test_registry[func_id]['metadata']['test_k'] = True
        
        return func(*args, **kwargs)
    
    wrapper._autopromptix_k = True
    return wrapper

def client(client_type: str) -> Callable:
    """
    Decorator to specify the AI client type
    
    Args:
        client_type: Type of client ('openai', 'anthropic', 'huggingface', etc.)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_id = f"{func.__module__}.{func.__name__}"
            
            if func_id not in _test_registry:
                _test_registry[func_id] = {
                    'function': func,
                    'metadata': {},
                    'test_results': []
                }
            
            _test_registry[func_id]['metadata']['client_type'] = client_type
            
            return func(*args, **kwargs)
        
        wrapper._autopromptix_client = client_type
        return wrapper
    
    return decorator

def get_test_registry() -> Dict[str, Any]:
    """Get the current test registry"""
    return _test_registry

def clear_test_registry():
    """Clear the test registry"""
    global _test_registry
    _test_registry = {}

def get_function_metadata(func_id: str) -> Dict[str, Any]:
    """Get metadata for a specific function"""
    return _test_registry.get(func_id, {}).get('metadata', {})

def get_function_test_results(func_id: str) -> List[Dict[str, Any]]:
    """Get test results for a specific function"""
    return _test_registry.get(func_id, {}).get('test_results', []) 