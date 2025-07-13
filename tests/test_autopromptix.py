"""
Comprehensive test suite for AutoPromptix
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
import json
import time

# Import AutoPromptix modules
import autopromptix
from autopromptix.storage import StorageManager
from autopromptix.prompt_improver import PromptImprover
from autopromptix.test_runner import TestRunner, TestResult
from autopromptix.decorators import get_test_registry, clear_test_registry
from autopromptix.server import AutoPromptixServer

class TestStorageManager:
    """Test the storage manager functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = StorageManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_storage_initialization(self):
        """Test storage manager initialization"""
        assert self.storage.storage_dir.exists()
        assert self.storage.knowledge_dir.exists()
        assert self.storage.chat_dir.exists()
        assert self.storage.improvement_dir.exists()
        assert self.storage.db_path.exists()
    
    def test_log_execution(self):
        """Test logging function execution"""
        self.storage.log_execution(
            "test.func", 
            ("arg1", "arg2"), 
            {"key": "value"}, 
            "result", 
            1.5, 
            True
        )
        
        history = self.storage.get_execution_history("test.func")
        assert len(history) == 1
        assert history[0]['function_id'] == "test.func"
        assert history[0]['success'] == True
    
    def test_save_prompt_improvement(self):
        """Test saving prompt improvements"""
        self.storage.save_prompt_improvement(
            "test.func",
            "original prompt",
            "improved prompt",
            "clarity improvement",
            0.85
        )
        
        improvements = self.storage.get_prompt_improvements("test.func")
        assert len(improvements) == 1
        assert improvements[0]['original_prompt'] == "original prompt"
        assert improvements[0]['improved_prompt'] == "improved prompt"
    
    def test_save_test_result(self):
        """Test saving test results"""
        self.storage.save_test_result(
            "test.func",
            "test_name",
            "v1",
            "expected",
            "actual",
            0.75,
            {"temperature": 0.7}
        )
        
        results = self.storage.get_test_results("test.func")
        assert len(results) == 1
        assert results[0]['test_name'] == "test_name"
        assert results[0]['score'] == 0.75

class TestPromptImprover:
    """Test the prompt improver functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = StorageManager(self.temp_dir)
        self.improver = PromptImprover(self.storage)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_parse_system_prompt(self):
        """Test system prompt parsing"""
        prompt = """
        You are a helpful assistant. 
        
        1. Always be polite
        2. Provide accurate information
        3. Be concise
        
        Do not provide harmful content.
        For example: "Hello, how can I help you?"
        """
        
        parsed = self.improver.parse_system_prompt(prompt)
        
        assert parsed['word_count'] > 0
        assert len(parsed['instructions']) >= 3
        assert len(parsed['constraints']) >= 1
        assert len(parsed['examples']) >= 1
    
    def test_analyze_prompt(self):
        """Test prompt analysis"""
        prompt = "You are a helpful assistant."
        
        analysis = self.improver.analyze_prompt(prompt)
        
        assert 0 <= analysis.clarity_score <= 1
        assert 0 <= analysis.specificity_score <= 1
        assert 0 <= analysis.completeness_score <= 1
        assert isinstance(analysis.potential_issues, list)
        assert isinstance(analysis.suggested_improvements, list)
    
    def test_improve_prompt(self):
        """Test prompt improvement"""
        original_prompt = "Be helpful."
        
        improvement = self.improver.improve_prompt(
            "test.func", 
            original_prompt, 
            improvement_type='clarity'
        )
        
        assert improvement.original_prompt == original_prompt
        assert improvement.improved_prompt != original_prompt
        assert improvement.confidence_score > 0
        assert improvement.expected_performance_gain >= 0

class TestTestRunner:
    """Test the test runner functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = StorageManager(self.temp_dir)
        self.improver = PromptImprover(self.storage)
        self.runner = TestRunner(self.storage, self.improver)
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_test_result_creation(self):
        """Test TestResult class"""
        result = TestResult("test.func", "test_name", "v1")
        
        assert result.function_id == "test.func"
        assert result.test_name == "test_name"
        assert result.prompt_version == "v1"
        assert result.success == False
        assert result.score == 0.0
        
        result.complete(True, "output", "expected", 0.8)
        
        assert result.success == True
        assert result.score == 0.8
        assert result.duration > 0
    
    def test_compare_outputs(self):
        """Test output comparison"""
        expected = "Hello, how are you?"
        actual = "Hello, how are you?"
        
        score = self.runner._compare_outputs(expected, actual)
        assert score == 1.0  # Exact match
        
        actual = "Hello, how are you doing?"
        score = self.runner._compare_outputs(expected, actual)
        assert 0 < score < 1.0  # Partial match
    
    def test_score_output_quality(self):
        """Test output quality scoring"""
        good_output = "This is a well-formed response with proper content."
        score = self.runner._score_output_quality(good_output)
        assert score > 0.5
        
        bad_output = "Error: Failed"
        score = self.runner._score_output_quality(bad_output)
        assert score < 0.8  # Should be lower due to error

class TestDecorators:
    """Test the decorator functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        clear_test_registry()
    
    def teardown_method(self):
        """Clean up test environment"""
        clear_test_registry()
    
    def test_selftest_decorator(self):
        """Test selftest decorator"""
        @autopromptix.selftest
        def test_func():
            return "test result"
        
        result = test_func()
        assert result == "test result"
        
        registry = get_test_registry()
        assert len(registry) == 1
        assert hasattr(test_func, '_autopromptix_selftest')
    
    def test_desiredoutput_decorator(self):
        """Test desiredoutput decorator"""
        @autopromptix.desiredoutput('/test/output.txt/@L5')
        def test_func():
            return "test result"
        
        result = test_func()
        assert result == "test result"
        assert hasattr(test_func, '_autopromptix_desiredoutput')
    
    def test_client_decorator(self):
        """Test client decorator"""
        @autopromptix.client('openai')
        def test_func():
            return "test result"
        
        result = test_func()
        assert result == "test result"
        assert hasattr(test_func, '_autopromptix_client')

class TestWebServer:
    """Test the web server functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.server = AutoPromptixServer(host='127.0.0.1', port=0)  # Port 0 = auto-assign
        self.client = self.server.app.test_client()
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        response = self.client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_functions' in data
        assert 'total_tests' in data
        assert 'avg_score' in data
    
    def test_functions_endpoint(self):
        """Test functions endpoint"""
        response = self.client.get('/api/functions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'functions' in data
        assert 'total' in data
    
    def test_settings_endpoint(self):
        """Test settings endpoint"""
        response = self.client.get('/api/settings')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'host' in data
        assert 'port' in data
        assert 'api_model' in data

# Integration tests
class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Setup test environment"""
        clear_test_registry()
    
    def teardown_method(self):
        """Clean up test environment"""
        clear_test_registry()
    
    def test_complete_workflow(self):
        """Test complete workflow from decoration to testing"""
        @autopromptix.selftest
        @autopromptix.client('test')
        def sample_function():
            return "Hello, I'm a test function!"
        
        # Run the function to register it
        result = sample_function()
        assert result == "Hello, I'm a test function!"
        
        # Check if it's registered
        registry = get_test_registry()
        assert len(registry) == 1
        
        func_id = list(registry.keys())[0]
        assert func_id in registry
        
        # Test the function metadata
        metadata = registry[func_id]['metadata']
        assert metadata.get('client_type') == 'test'
    
    def test_storage_integration(self):
        """Test storage integration with other components"""
        storage = StorageManager()
        
        # Test saving and retrieving data
        storage.log_execution("test.func", (), {}, "result", 1.0, True)
        history = storage.get_execution_history("test.func")
        
        assert len(history) == 1
        assert history[0]['function_id'] == "test.func"
        
        # Test stats
        stats = storage.get_function_stats("test.func")
        assert stats['execution_count'] == 1

def run_manual_tests():
    """Run manual tests that require human verification"""
    print("🧪 Running Manual Tests...")
    
    # Test 1: Basic import and setup
    print("1. Testing basic import...")
    try:
        import autopromptix
        print("   ✅ Import successful")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
    
    # Test 2: Server startup (mock)
    print("2. Testing server initialization...")
    try:
        server = AutoPromptixServer(port=0)  # Port 0 = auto-assign
        print("   ✅ Server initialization successful")
    except Exception as e:
        print(f"   ❌ Server initialization failed: {e}")
    
    # Test 3: Decorator registration
    print("3. Testing decorator registration...")
    try:
        @autopromptix.selftest
        def test_func():
            return "test"
        
        result = test_func()
        registry = get_test_registry()
        print(f"   ✅ Decorator registration successful, {len(registry)} functions registered")
    except Exception as e:
        print(f"   ❌ Decorator registration failed: {e}")
    
    print("✅ Manual tests completed!")

if __name__ == "__main__":
    # Run manual tests
    run_manual_tests()
    
    # Run pytest if available
    try:
        import pytest
        print("\n🚀 Running pytest suite...")
        pytest.main([__file__, "-v"])
    except ImportError:
        print("\n📝 Install pytest to run automated tests: pip install pytest")
        print("For now, running manual tests only.") 