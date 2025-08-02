"""
AutoPromptix Test Runner

Handles automated testing of prompts with improvements and iterative testing.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from .storage import StorageManager
from .prompt_improver import PromptImprover, PromptImprovement
from .decorators import get_test_registry, get_function_metadata

class TestResult:
    """Represents a single test result"""
    
    def __init__(self, function_id: str, test_name: str, prompt_version: str):
        self.function_id = function_id
        self.test_name = test_name
        self.prompt_version = prompt_version
        self.start_time = time.time()
        self.end_time = None
        self.success = False
        self.error = None
        self.actual_output = None
        self.expected_output = None
        self.score = 0.0
        self.metadata = {}
    
    def complete(self, success: bool, actual_output: Any = None, 
                expected_output: Any = None, score: float = 0.0, 
                error: str = None, metadata: Dict[str, Any] = None):
        """Mark test as complete"""
        self.end_time = time.time()
        self.success = success
        self.actual_output = actual_output
        self.expected_output = expected_output
        self.score = score
        self.error = error
        self.metadata = metadata or {}
    
    @property
    def duration(self) -> float:
        """Get test duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'function_id': self.function_id,
            'test_name': self.test_name,
            'prompt_version': self.prompt_version,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'success': self.success,
            'actual_output': self.actual_output,
            'expected_output': self.expected_output,
            'score': self.score,
            'error': self.error,
            'metadata': self.metadata
        }

class TestRunner:
    """Handles automated testing of prompts with improvements"""
    
    def __init__(self, storage_manager: StorageManager, prompt_improver: PromptImprover):
        self.storage = storage_manager
        self.prompt_improver = prompt_improver
        self.active_tests = {}
        self.test_results = []
        self.test_callbacks = []
    
    def add_test_callback(self, callback: Callable[[TestResult], None]):
        """Add a callback to be called when tests complete"""
        self.test_callbacks.append(callback)
    
    def run_automated_tests(self, function_id: str, max_iterations: int = 10) -> List[TestResult]:
        """
        Run automated tests for a function with prompt improvements
        
        Args:
            function_id: ID of the function to test
            max_iterations: Maximum number of improvement iterations
            
        Returns:
            List of test results
        """
        registry = get_test_registry()
        if function_id not in registry:
            raise ValueError(f"Function {function_id} not found in test registry")
        
        function_info = registry[function_id]
        metadata = function_info['metadata']
        
        results = []
        current_prompt = self._extract_current_prompt(function_info)
        
        for iteration in range(max_iterations):
            print(f"Running test iteration {iteration + 1}/{max_iterations} for {function_id}")
            
            # Run tests with current prompt
            iteration_results = self._run_function_tests(function_id, current_prompt, f"v{iteration}")
            results.extend(iteration_results)
            
            # Calculate average score for this iteration
            avg_score = sum(r.score for r in iteration_results) / len(iteration_results) if iteration_results else 0
            
            # Check if we should stop (good enough performance)
            if avg_score >= 0.85:
                print(f"Stopping early - achieved target score {avg_score:.2f}")
                break
            
            # Improve prompt based on results
            if iteration < max_iterations - 1:  # Don't improve on last iteration
                try:
                    improvement = self.prompt_improver.improve_prompt(
                        function_id, current_prompt, iteration_results
                    )
                    current_prompt = improvement.improved_prompt
                    print(f"Improved prompt: {improvement.improvement_reason}")
                except Exception as e:
                    print(f"Failed to improve prompt: {e}")
                    break
        
        # Save all results
        for result in results:
            self.storage.save_test_result(
                result.function_id, result.test_name, result.prompt_version,
                str(result.expected_output), str(result.actual_output), 
                result.score, result.metadata
            )
        
        return results
    
    def _extract_current_prompt(self, function_info: Dict[str, Any]) -> str:
        """Extract current prompt from function info"""
        # Try to find prompt in function source code
        func = function_info['function']
        source_code = self._get_function_source(func)
        
        # Look for system prompt in common patterns
        prompt_patterns = [
            r'system.*?content.*?["\']([^"\']+)["\']',
            r'prompt\s*=\s*["\']([^"\']+)["\']',
            r'system_prompt\s*=\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in prompt_patterns:
            import re
            match = re.search(pattern, source_code, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)
        
        # Default prompt if none found
        return "You are a helpful assistant."
    
    def _get_function_source(self, func: Callable) -> str:
        """Get source code of a function"""
        try:
            import inspect
            return inspect.getsource(func)
        except:
            return ""
    
    def _run_function_tests(self, function_id: str, prompt: str, version: str) -> List[TestResult]:
        """Run tests for a function with a specific prompt"""
        registry = get_test_registry()
        function_info = registry[function_id]
        metadata = function_info['metadata']
        
        results = []
        
        # Run different types of tests based on metadata
        if metadata.get('test_system_prompt'):
            results.extend(self._run_system_prompt_tests(function_id, prompt, version))
        
        if metadata.get('test_temperature'):
            results.extend(self._run_temperature_tests(function_id, prompt, version))
        
        if metadata.get('test_k'):
            results.extend(self._run_k_tests(function_id, prompt, version))
        
        if metadata.get('desired_output'):
            results.extend(self._run_output_tests(function_id, prompt, version, metadata['desired_output']))
        
        # Run basic functionality tests
        if not results:
            results.extend(self._run_basic_tests(function_id, prompt, version))
        
        return results
    
    def _run_system_prompt_tests(self, function_id: str, prompt: str, version: str) -> List[TestResult]:
        """Run system prompt tests"""
        test_prompts = [
            prompt,
            prompt + "\n\nBe concise and specific.",
            prompt + "\n\nProvide detailed explanations.",
            prompt + "\n\nFocus on accuracy and clarity."
        ]
        
        results = []
        for i, test_prompt in enumerate(test_prompts):
            result = TestResult(function_id, f"system_prompt_test_{i}", version)
            
            try:
                # Execute function with modified prompt
                score = self._execute_function_with_prompt(function_id, test_prompt)
                result.complete(True, score=score)
            except Exception as e:
                result.complete(False, error=str(e))
            
            results.append(result)
        
        return results
    
    def _run_temperature_tests(self, function_id: str, prompt: str, version: str) -> List[TestResult]:
        """Run temperature tests"""
        temperatures = [0.1, 0.5, 0.7, 1.0]
        results = []
        
        for temp in temperatures:
            result = TestResult(function_id, f"temperature_test_{temp}", version)
            
            try:
                score = self._execute_function_with_temperature(function_id, prompt, temp)
                result.complete(True, score=score, metadata={'temperature': temp})
            except Exception as e:
                result.complete(False, error=str(e))
            
            results.append(result)
        
        return results
    
    def _run_k_tests(self, function_id: str, prompt: str, version: str) -> List[TestResult]:
        """Run top-k tests"""
        k_values = [1, 5, 10, 20]
        results = []
        
        for k in k_values:
            result = TestResult(function_id, f"k_test_{k}", version)
            
            try:
                score = self._execute_function_with_k(function_id, prompt, k)
                result.complete(True, score=score, metadata={'top_k': k})
            except Exception as e:
                result.complete(False, error=str(e))
            
            results.append(result)
        
        return results
    
    def _run_output_tests(self, function_id: str, prompt: str, version: str, 
                         desired_output: Dict[str, Any]) -> List[TestResult]:
        """Run tests against desired output"""
        result = TestResult(function_id, "output_comparison", version)
        
        try:
            # Load expected output
            expected = self._load_expected_output(desired_output)
            
            # Execute function
            actual = self._execute_function_basic(function_id, prompt)
            
            # Compare outputs
            score = self._compare_outputs(expected, actual)
            
            result.complete(True, actual_output=actual, expected_output=expected, score=score)
        except Exception as e:
            result.complete(False, error=str(e))
        
        return [result]
    
    def _run_basic_tests(self, function_id: str, prompt: str, version: str) -> List[TestResult]:
        """Run basic functionality tests"""
        result = TestResult(function_id, "basic_execution", version)
        
        try:
            output = self._execute_function_basic(function_id, prompt)
            # Basic scoring based on output quality
            score = self._score_output_quality(output)
            result.complete(True, actual_output=output, score=score)
        except Exception as e:
            result.complete(False, error=str(e))
        
        return [result]
    
    def _execute_function_with_prompt(self, function_id: str, prompt: str) -> float:
        """Execute function with specific prompt and return score"""
        # This is a simplified implementation
        # In reality, you'd need to modify the function's system prompt
        registry = get_test_registry()
        func = registry[function_id]['function']
        
        # Execute function
        try:
            result = func()
            return self._score_output_quality(result)
        except Exception as e:
            return 0.0
    
    def _execute_function_with_temperature(self, function_id: str, prompt: str, temperature: float) -> float:
        """Execute function with specific temperature"""
        # Simplified - would need actual LLM integration
        return self._execute_function_with_prompt(function_id, prompt) * (1 - abs(temperature - 0.7) * 0.1)
    
    def _execute_function_with_k(self, function_id: str, prompt: str, k: int) -> float:
        """Execute function with specific top-k value"""
        # Simplified - would need actual LLM integration
        return self._execute_function_with_prompt(function_id, prompt) * (1 - abs(k - 10) * 0.01)
    
    def _execute_function_basic(self, function_id: str, prompt: str) -> Any:
        """Execute function with basic setup"""
        registry = get_test_registry()
        func = registry[function_id]['function']
        
        try:
            return func()
        except Exception as e:
            return f"Error: {e}"
    
    def _load_expected_output(self, desired_output: Dict[str, Any]) -> str:
        """Load expected output from file"""
        file_path = desired_output['file_path']
        line_ref = desired_output.get('line_ref')
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            if line_ref:
                lines = content.split('\n')
                if line_ref <= len(lines):
                    return lines[line_ref - 1]
            
            return content.strip()
        except Exception as e:
            return f"Error loading expected output: {e}"
    
    def _compare_outputs(self, expected: str, actual: str) -> float:
        """Compare expected and actual outputs, return similarity score"""
        if not expected or not actual:
            return 0.0
        
        # Simple similarity scoring
        expected_words = set(expected.lower().split())
        actual_words = set(str(actual).lower().split())
        
        if not expected_words:
            return 1.0 if not actual_words else 0.0
        
        intersection = expected_words.intersection(actual_words)
        union = expected_words.union(actual_words)
        
        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 0.0
        
        # Exact match bonus
        if expected.strip().lower() == str(actual).strip().lower():
            return 1.0
        
        return jaccard
    
    def _score_output_quality(self, output: Any) -> float:
        """Score output quality based on various factors"""
        if output is None:
            return 0.0
        
        output_str = str(output)
        
        # Basic quality indicators
        score = 0.5  # Base score
        
        # Length check (not too short, not too long)
        if 10 <= len(output_str) <= 1000:
            score += 0.2
        
        # Contains meaningful content
        if any(word in output_str.lower() for word in ['the', 'and', 'or', 'but', 'if', 'then']):
            score += 0.1
        
        # No obvious errors
        if 'error' not in output_str.lower() and 'exception' not in output_str.lower():
            score += 0.1
        
        # Proper formatting
        if output_str.strip() == output_str:
            score += 0.1
        
        return min(score, 1.0)
    
    def get_test_results(self, function_id: str) -> List[Dict[str, Any]]:
        """Get test results for a function"""
        return self.storage.get_test_results(function_id)
    
    def get_function_performance(self, function_id: str) -> Dict[str, Any]:
        """Get performance metrics for a function"""
        results = self.get_test_results(function_id)
        
        if not results:
            return {'total_tests': 0, 'avg_score': 0.0, 'success_rate': 0.0}
        
        total_tests = len(results)
        avg_score = sum(r.get('score', 0) for r in results) / total_tests
        successful_tests = sum(1 for r in results if r.get('score', 0) > 0.5)
        success_rate = successful_tests / total_tests
        
        return {
            'total_tests': total_tests,
            'avg_score': avg_score,
            'success_rate': success_rate,
            'latest_score': results[0].get('score', 0) if results else 0
        }
    
    def run_single_test(self, function_id: str, test_name: str, 
                       prompt: str = None, config: Dict[str, Any] = None) -> TestResult:
        """Run a single test for a function"""
        if prompt is None:
            registry = get_test_registry()
            if function_id in registry:
                prompt = self._extract_current_prompt(registry[function_id])
            else:
                prompt = "You are a helpful assistant."
        
        result = TestResult(function_id, test_name, "manual")
        
        try:
            output = self._execute_function_basic(function_id, prompt)
            score = self._score_output_quality(output)
            result.complete(True, actual_output=output, score=score, metadata=config or {})
        except Exception as e:
            result.complete(False, error=str(e))
        
        # Save result
        self.storage.save_test_result(
            result.function_id, result.test_name, result.prompt_version,
            str(result.expected_output), str(result.actual_output), 
            result.score, result.metadata
        )
        
        # Notify callbacks
        for callback in self.test_callbacks:
            try:
                callback(result)
            except Exception as e:
                print(f"Error in test callback: {e}")
        
        return result
    
    async def run_async_test(self, function_id: str, test_name: str, 
                            prompt: str = None, config: Dict[str, Any] = None) -> TestResult:
        """Run an async test for a function"""
        # For now, just wrap the sync version
        return self.run_single_test(function_id, test_name, prompt, config) 