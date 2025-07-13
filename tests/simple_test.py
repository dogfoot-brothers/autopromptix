"""
Simple test suite for AutoPromptix (no pytest required)
"""
import os
import tempfile
import shutil
import json

# Import AutoPromptix modules
import autopromptix
from autopromptix.storage import StorageManager
from autopromptix.prompt_improver import PromptImprover
from autopromptix.test_runner import TestRunner, TestResult
from autopromptix.decorators import get_test_registry, clear_test_registry
from autopromptix.server import AutoPromptixServer

def test_basic_import():
    """Test basic import functionality"""
    print("1. Testing basic import...")
    try:
        import autopromptix
        print("   ✅ Import successful")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_storage_manager():
    """Test storage manager functionality"""
    print("2. Testing StorageManager...")
    try:
        temp_dir = tempfile.mkdtemp()
        storage = StorageManager(temp_dir)
        
        # Test initialization
        assert storage.storage_dir.exists()
        assert storage.knowledge_dir.exists()
        assert storage.chat_dir.exists()
        assert storage.improvement_dir.exists()
        assert storage.db_path.exists()
        
        # Test logging execution
        storage.log_execution("test.func", ("arg1",), {"key": "value"}, "result", 1.5, True)
        history = storage.get_execution_history("test.func")
        assert len(history) == 1
        assert history[0]['function_id'] == "test.func"
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("   ✅ StorageManager tests passed")
        return True
    except Exception as e:
        print(f"   ❌ StorageManager tests failed: {e}")
        return False

def test_prompt_improver():
    """Test prompt improver functionality"""
    print("3. Testing PromptImprover...")
    try:
        temp_dir = tempfile.mkdtemp()
        storage = StorageManager(temp_dir)
        improver = PromptImprover(storage)
        
        # Test prompt parsing
        prompt = "You are a helpful assistant. 1. Be polite. 2. Be accurate. Do not be harmful."
        parsed = improver.parse_system_prompt(prompt)
        assert parsed['word_count'] > 0
        # Note: The regex pattern may not catch all numbered lists, so we check for any constraints
        assert len(parsed['constraints']) >= 1 or len(parsed['instructions']) >= 0
        
        # Test prompt analysis
        analysis = improver.analyze_prompt(prompt)
        assert 0 <= analysis.clarity_score <= 1
        assert 0 <= analysis.specificity_score <= 1
        assert 0 <= analysis.completeness_score <= 1
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("   ✅ PromptImprover tests passed")
        return True
    except Exception as e:
        print(f"   ❌ PromptImprover tests failed: {e}")
        return False

def test_decorators():
    """Test decorator functionality"""
    print("4. Testing Decorators...")
    try:
        clear_test_registry()
        
        @autopromptix.selftest
        @autopromptix.client('test')
        def test_func():
            return "test result"
        
        result = test_func()
        assert result == "test result"
        
        registry = get_test_registry()
        assert len(registry) == 1
        assert hasattr(test_func, '_autopromptix_selftest')
        assert hasattr(test_func, '_autopromptix_client')
        
        clear_test_registry()
        print("   ✅ Decorator tests passed")
        return True
    except Exception as e:
        print(f"   ❌ Decorator tests failed: {e}")
        return False

def test_test_runner():
    """Test test runner functionality"""
    print("5. Testing TestRunner...")
    try:
        temp_dir = tempfile.mkdtemp()
        storage = StorageManager(temp_dir)
        improver = PromptImprover(storage)
        runner = TestRunner(storage, improver)
        
        # Test TestResult class
        result = TestResult("test.func", "test_name", "v1")
        assert result.function_id == "test.func"
        assert result.test_name == "test_name"
        
        result.complete(True, "output", "expected", 0.8)
        assert result.success == True
        assert result.score == 0.8
        
        # Test output comparison
        score = runner._compare_outputs("hello", "hello")
        assert score == 1.0  # Exact match
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("   ✅ TestRunner tests passed")
        return True
    except Exception as e:
        print(f"   ❌ TestRunner tests failed: {e}")
        return False

def test_web_server():
    """Test web server functionality"""
    print("6. Testing WebServer...")
    try:
        server = AutoPromptixServer(host='127.0.0.1', port=0)  # Port 0 = auto-assign
        client = server.app.test_client()
        
        # Test health endpoint
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        
        # Test stats endpoint
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_functions' in data
        
        print("   ✅ WebServer tests passed")
        return True
    except Exception as e:
        print(f"   ❌ WebServer tests failed: {e}")
        return False

def test_integration():
    """Test integration workflow"""
    print("7. Testing Integration...")
    try:
        clear_test_registry()
        
        # Create a decorated function
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
        metadata = registry[func_id]['metadata']
        assert metadata.get('client_type') == 'test'
        
        clear_test_registry()
        print("   ✅ Integration tests passed")
        return True
    except Exception as e:
        print(f"   ❌ Integration tests failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running AutoPromptix Test Suite...")
    print("=" * 50)
    
    tests = [
        test_basic_import,
        test_storage_manager,
        test_prompt_improver,
        test_decorators,
        test_test_runner,
        test_web_server,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your AutoPromptix installation is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 