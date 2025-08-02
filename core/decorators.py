"""
Enhanced AutoPromptix Decorators

Simplified decorator system for better usability and cleaner code.
"""

import functools
import inspect
import json
import os
from typing import Callable, Any, Dict, List, Optional, Union
from pathlib import Path
from .storage import StorageManager

# Global registry for decorated functions
_test_registry = {}

def _get_storage():
    """Get the storage manager instance"""
    from . import storage
    return storage

def test(
    expected_output: Optional[str] = None,
    test_types: Optional[List[str]] = None,
    client: str = 'openai',
    max_iterations: int = 10,
    target_score: float = 0.85,
    auto_improve: bool = True,
    prompt_variations: Optional[List[str]] = None,
    config_file: Optional[str] = None
) -> Callable:
    """
    Unified decorator for AutoPromptix testing
    
    Args:
        expected_output: Path to expected output file (e.g., './output.txt/@L31')
        test_types: List of test types ['system_prompt', 'temperature', 'top_k']
        client: AI client type ('openai', 'anthropic', 'huggingface')
        max_iterations: Maximum improvement iterations
        target_score: Target score to stop improving
        auto_improve: Whether to automatically improve prompts
        prompt_variations: List of prompt variations to test
        config_file: Path to configuration file
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function ID
            func_id = f"{func.__module__}.{func.__name__}"
            
            # Initialize function in registry
            if func_id not in _test_registry:
                _test_registry[func_id] = {
                    'function': func,
                    'metadata': {},
                    'test_results': []
                }
            
            # Initialize local variables with decorator parameters
            local_expected_output = expected_output
            local_test_types = test_types
            local_client = client
            local_max_iterations = max_iterations
            local_target_score = target_score
            local_auto_improve = auto_improve
            local_prompt_variations = prompt_variations
            
            # Load config from file if provided
            if config_file and os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                local_expected_output = config.get('expected_output', local_expected_output)
                local_test_types = config.get('test_types', local_test_types)
                local_client = config.get('client', local_client)
                local_max_iterations = config.get('max_iterations', local_max_iterations)
                local_target_score = config.get('target_score', local_target_score)
                local_auto_improve = config.get('auto_improve', local_auto_improve)
                local_prompt_variations = config.get('prompt_variations', local_prompt_variations)
            
            # Store metadata
            metadata = _test_registry[func_id]['metadata']
            metadata.update({
                'expected_output': local_expected_output,
                'test_types': local_test_types or ['basic'],
                'client_type': local_client,
                'max_iterations': local_max_iterations,
                'target_score': local_target_score,
                'auto_improve': local_auto_improve,
                'prompt_variations': local_prompt_variations
            })
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Log execution
            storage = _get_storage()
            storage.log_execution(func_id, args, kwargs, result)
            
            return result
        
        # Store decorator info for introspection
        wrapper._autopromptix_test = {
            'expected_output': expected_output,
            'test_types': test_types,
            'client': client,
            'max_iterations': max_iterations,
            'target_score': target_score,
            'auto_improve': auto_improve,
            'prompt_variations': prompt_variations,
            'config_file': config_file
        }
        
        return wrapper
    
    return decorator

def test_config(config_path: str) -> Callable:
    """
    Decorator using external configuration file
    
    Args:
        config_path: Path to JSON/YAML configuration file
    """
    def decorator(func: Callable) -> Callable:
        return test(config_file=config_path)(func)
    
    return decorator

def prompt_template(template_path: str) -> Callable:
    """
    Decorator using prompt template file
    
    Args:
        template_path: Path to prompt template file
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Load prompt template
            template = _load_prompt_template(template_path)
            
            # Apply template to function
            func_id = f"{func.__module__}.{func.__name__}"
            
            if func_id not in _test_registry:
                _test_registry[func_id] = {
                    'function': func,
                    'metadata': {},
                    'test_results': []
                }
            
            # Store template info
            _test_registry[func_id]['metadata'].update({
                'template_path': template_path,
                'template': template,
                'expected_output': template.get('expected_output'),
                'test_types': template.get('test_types', ['system_prompt']),
                'prompt_variations': template.get('variations', [])
            })
            
            return func(*args, **kwargs)
        
        wrapper._autopromptix_template = template_path
        return wrapper
    
    return decorator

def _load_prompt_template(template_path: str) -> Dict[str, Any]:
    """Load prompt template from file"""
    try:
        with open(template_path, 'r') as f:
            if template_path.endswith('.json'):
                return json.load(f)
            elif template_path.endswith('.yaml') or template_path.endswith('.yml'):
                import yaml
                return yaml.safe_load(f)
            else:
                # Assume JSON
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load template {template_path}: {e}")
        return {}

class test_context:
    """Context manager for test configuration"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
        self.original_registry = {}
    
    def __enter__(self):
        # Store original registry
        self.original_registry = _test_registry.copy()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original registry
        global _test_registry
        _test_registry = self.original_registry

def auto_test(func: Callable) -> Callable:
    """
    Automatic test decorator that detects prompts from function source
    
    Args:
        func: Function to decorate
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_id = f"{func.__module__}.{func.__name__}"
        
        # Auto-detect prompts from function source
        source_code = inspect.getsource(func)
        prompts = _extract_prompts_from_source(source_code)
        
        # Initialize with auto-detected settings
        if func_id not in _test_registry:
            _test_registry[func_id] = {
                'function': func,
                'metadata': {
                    'auto_detected': True,
                    'detected_prompts': prompts,
                    'test_types': ['system_prompt'],
                    'auto_improve': True
                },
                'test_results': []
            }
        
        result = func(*args, **kwargs)
        
        # Log execution
        storage = _get_storage()
        storage.log_execution(func_id, args, kwargs, result)
        
        return result
    
    wrapper._autopromptix_auto_test = True
    return wrapper

def _extract_prompts_from_source(source_code: str) -> List[str]:
    """Extract prompts from function source code"""
    import re
    
    prompts = []
    
    # Look for system prompts
    system_patterns = [
        r'system.*?content.*?["\']([^"\']+)["\']',
        r'prompt\s*=\s*["\']([^"\']+)["\']',
        r'system_prompt\s*=\s*["\']([^"\']+)["\']'
    ]
    
    for pattern in system_patterns:
        matches = re.findall(pattern, source_code, re.IGNORECASE | re.DOTALL)
        prompts.extend(matches)
    
    return list(set(prompts))  # Remove duplicates

def autopromptix(
    role: str = "assistant",
    temperature: float = 0.7,
    max_tokens: int = 100,
    test_data_pool: Optional[str] = None,
    **kwargs
) -> Callable:
    """
    Main AutoPromptix decorator for function testing and improvement
    
    Args:
        role: The role for the AI assistant
        temperature: Temperature for AI responses
        max_tokens: Maximum tokens for responses
        test_data_pool: Name of test data pool to use
        **kwargs: Additional configuration options
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function ID
            func_id = f"{func.__module__}.{func.__name__}"
            
            # Initialize function in registry
            if func_id not in _test_registry:
                _test_registry[func_id] = {
                    'function': func,
                    'metadata': {},
                    'test_results': []
                }
            
            # Store metadata
            metadata = _test_registry[func_id]['metadata']
            metadata.update({
                'role': role,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'test_data_pool': test_data_pool,
                **kwargs
            })
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Log execution
            storage = _get_storage()
            storage.log_execution(func_id, args, kwargs, result)
            
            return result
        
        # Store decorator info for introspection
        wrapper._autopromptix = {
            'role': role,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'test_data_pool': test_data_pool,
            **kwargs
        }
        
        return wrapper
    
    return decorator

# Backward compatibility aliases
selftest = test
desiredoutput = lambda path: test(expected_output=path)
self_test_system_prompt = lambda func: test(test_types=['system_prompt'])(func)
self_test_temperature = lambda func: test(test_types=['temperature'])(func)
self_test_k = lambda func: test(test_types=['top_k'])(func)
client = lambda client_type: test(client=client_type)

# Registry functions
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