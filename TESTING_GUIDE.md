# 🧪 AutoPromptix Testing Guide

This guide covers different testing strategies for the AutoPromptix project, from basic functionality tests to end-to-end integration testing.

## 📋 Test Levels Overview

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test component interactions
3. **API Tests** - Test web server endpoints
4. **End-to-End Tests** - Test complete workflows
5. **Manual Tests** - Interactive testing and validation
6. **Performance Tests** - Load and stress testing

---

## 🚀 Quick Start Testing

### 1. Basic Functionality Test

Run this first to verify your installation:

```bash
python simple_test.py
```

This will test:
- ✅ Package imports
- ✅ Storage manager
- ✅ Prompt improver  
- ✅ Decorators
- ✅ Test runner
- ✅ Web server
- ✅ Integration workflow

### 2. Run the Main Example

```bash
python main.py
```

This will:
- Start the AutoPromptix server
- Register a sample function
- Run the greeting function
- Open dashboard at `http://127.0.0.1:8000`

---

## 🔧 Detailed Testing Instructions

### Unit Tests

#### Test Storage Manager
```python
from autopromptix.storage import StorageManager
import tempfile

# Create temporary storage
temp_dir = tempfile.mkdtemp()
storage = StorageManager(temp_dir)

# Test logging
storage.log_execution("test.func", (), {}, "result", 1.0, True)
history = storage.get_execution_history("test.func")
assert len(history) == 1
```

#### Test Prompt Improver
```python
from autopromptix.prompt_improver import PromptImprover

improver = PromptImprover(storage)

# Test prompt analysis
prompt = "You are a helpful assistant. Be polite and accurate."
analysis = improver.analyze_prompt(prompt)
print(f"Clarity: {analysis.clarity_score}")
print(f"Issues: {analysis.potential_issues}")
```

#### Test Decorators
```python
import autopromptix
from autopromptix.decorators import get_test_registry, clear_test_registry

clear_test_registry()

@autopromptix.selftest
@autopromptix.client('test')
def test_function():
    return "Hello, World!"

result = test_function()
registry = get_test_registry()
assert len(registry) == 1
```

### Integration Tests

#### Test Complete Workflow
```python
# 1. Define decorated function
@autopromptix.selftest
@autopromptix.desiredoutput('./output.txt/@L31')
def greeting():
    return "Hello, how are you?"

# 2. Run function to register it
result = greeting()

# 3. Check registration
registry = get_test_registry()
assert len(registry) == 1

# 4. Run automated tests
from autopromptix import test_runner
test_results = test_runner.run_single_test(
    list(registry.keys())[0], 
    "integration_test"
)
```

### API Tests

#### Test Web Server Endpoints
```python
from autopromptix.server import AutoPromptixServer
import json

server = AutoPromptixServer(port=0)
client = server.app.test_client()

# Test health endpoint
response = client.get('/api/health')
assert response.status_code == 200
data = json.loads(response.data)
assert data['status'] == 'healthy'

# Test functions endpoint
response = client.get('/api/functions')
assert response.status_code == 200

# Test settings
response = client.get('/api/settings')
assert response.status_code == 200
```

---

## 🌐 Manual Testing Procedures

### 1. Web Dashboard Testing

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Open browser to:** `http://127.0.0.1:8000`

3. **Verify dashboard elements:**
   - [ ] Statistics cards display correctly
   - [ ] Functions list appears
   - [ ] "Run Test" buttons work
   - [ ] "Auto Test" buttons work
   - [ ] Real-time updates work

### 2. API Testing with curl

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Get functions
curl http://127.0.0.1:8000/api/functions

# Get statistics
curl http://127.0.0.1:8000/api/stats

# Run a test (if functions exist)
curl -X POST http://127.0.0.1:8000/api/functions/main.greeting/test \
  -H "Content-Type: application/json" \
  -d '{"test_name": "manual_test"}'
```

### 3. Prompt Testing

Test different prompt scenarios:

#### Simple Prompt
```python
@autopromptix.selftest
def simple_prompt():
    # Test with basic prompt
    return "Simple response"
```

#### Complex Prompt
```python
@autopromptix.selftest
@autopromptix.self_test_system_prompt
@autopromptix.self_test_temperature
def complex_prompt():
    # Test with detailed prompt
    return openai.chat.completions.create(...)
```

#### With Desired Output
```python
@autopromptix.selftest
@autopromptix.desiredoutput('./expected.txt/@L1')
def output_test():
    return "Expected output"
```

---

## 🚦 Testing Scenarios

### Scenario 1: New Function Registration

1. Create a new function with decorators
2. Run the function
3. Check web dashboard
4. Verify function appears in list
5. Run manual test
6. Check test results

### Scenario 2: Prompt Improvement

1. Create function with basic prompt
2. Run automated tests
3. Check improvement suggestions
4. Apply improvements
5. Re-run tests
6. Compare scores

### Scenario 3: Multiple Iterations

1. Set `max_test_n = 3`
2. Run automated tests
3. Monitor improvement progression
4. Check final vs initial scores
5. Review improvement history

### Scenario 4: Error Handling

1. Test with invalid OpenAI key
2. Test with unreachable endpoints
3. Test with malformed requests
4. Verify graceful error handling

---

## 📊 Performance Testing

### Load Testing

Test the web server under load:

```python
import concurrent.futures
import requests
import time

def test_endpoint():
    response = requests.get('http://127.0.0.1:8000/api/health')
    return response.status_code == 200

# Run 100 concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_endpoint) for _ in range(100)]
    results = [f.result() for f in futures]
    success_rate = sum(results) / len(results)
    print(f"Success rate: {success_rate * 100}%")
```

### Storage Performance

Test storage operations:

```python
import time
from autopromptix.storage import StorageManager

storage = StorageManager()

# Test bulk operations
start_time = time.time()
for i in range(1000):
    storage.log_execution(f"test.func_{i}", (), {}, f"result_{i}", 0.1, True)
duration = time.time() - start_time
print(f"1000 storage operations took {duration:.2f} seconds")
```

---

## ⚠️ Common Issues & Troubleshooting

### Issue: Import Errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: Port Already in Use
```python
# Solution: Use different port
autopromptix.start_server(port=8001)
```

### Issue: Database Locked
```python
# Solution: Close existing connections
storage.cleanup_old_data()
```

### Issue: Tests Fail
```bash
# Solution: Run debug test
python debug_test.py
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Storage Contents
```python
from autopromptix import storage
print(storage.get_all_functions())
print(storage.get_function_stats("your.function"))
```

### Monitor Test Registry
```python
from autopromptix.decorators import get_test_registry
print(get_test_registry())
```

### Inspect Database
```bash
sqlite3 autopromptix_data/autopromptix.db
.tables
SELECT * FROM test_executions LIMIT 5;
```

---

## 📝 Test Checklist

### Before Release
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Web server starts correctly
- [ ] Dashboard loads and functions
- [ ] API endpoints respond correctly
- [ ] Error handling works
- [ ] Storage operations work
- [ ] Decorators register functions
- [ ] Test runner executes tests
- [ ] Prompt improver analyzes prompts
- [ ] Documentation is accurate

### Performance Checklist
- [ ] Server handles 100+ concurrent requests
- [ ] Storage operations complete within 1 second
- [ ] Memory usage stays reasonable
- [ ] No memory leaks detected
- [ ] Database operations are efficient

### Security Checklist
- [ ] No sensitive data in logs
- [ ] Input validation works
- [ ] Error messages don't leak info
- [ ] File operations are safe
- [ ] Database queries are safe

---

## 🎯 Advanced Testing

### Custom Test Framework

Create your own test runner:

```python
from autopromptix import test_runner, storage

# Custom test configuration
config = {
    'temperature': [0.1, 0.5, 0.9],
    'top_k': [1, 5, 10],
    'prompts': [
        "You are helpful.",
        "You are a detailed assistant.",
        "You are concise and accurate."
    ]
}

# Run custom tests
for temp in config['temperature']:
    for k in config['top_k']:
        for prompt in config['prompts']:
            result = test_runner.run_single_test(
                'your.function',
                f'custom_temp_{temp}_k_{k}',
                prompt,
                {'temperature': temp, 'top_k': k}
            )
            print(f"Score: {result.score} for temp={temp}, k={k}")
```

### A/B Testing

Compare different prompt versions:

```python
def compare_prompts(prompt_a, prompt_b, num_tests=10):
    scores_a = []
    scores_b = []
    
    for i in range(num_tests):
        result_a = test_runner.run_single_test(
            'test.function', f'prompt_a_{i}', prompt_a
        )
        result_b = test_runner.run_single_test(
            'test.function', f'prompt_b_{i}', prompt_b
        )
        
        scores_a.append(result_a.score)
        scores_b.append(result_b.score)
    
    avg_a = sum(scores_a) / len(scores_a)
    avg_b = sum(scores_b) / len(scores_b)
    
    print(f"Prompt A average: {avg_a:.3f}")
    print(f"Prompt B average: {avg_b:.3f}")
    print(f"Winner: {'A' if avg_a > avg_b else 'B'}")
```

---

## 📚 Additional Resources

- **pytest**: For professional test suites
- **locust**: For load testing
- **pytest-cov**: For coverage reporting
- **black**: For code formatting in tests
- **mypy**: For type checking

Install testing dependencies:
```bash
pip install pytest pytest-cov locust black mypy
```

Run comprehensive tests with coverage:
```bash
pytest test_autopromptix.py --cov=autopromptix --cov-report=html
``` 