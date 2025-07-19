# AutoPromptix

**Enhanced Automated Prompt Testing and Improvement Tool**

AutoPromptix is a comprehensive web-based server for testing and improving AI prompts automatically. It provides an enhanced decorator-based system for marking functions for testing and includes a beautiful web dashboard for monitoring and managing prompt improvements.

## ✨ Features

- 🔄 **Automated Testing**: Run tests with different prompt configurations
- 📊 **Prompt Analysis**: Parse and analyze system prompts for quality metrics
- 🚀 **Prompt Improvement**: Automatically improve prompts based on test results
- 📈 **Performance Tracking**: Track prompt performance over time
- 🌐 **Enhanced Web Dashboard**: Beautiful web interface with real-time editing
- 💾 **Local Storage**: Save knowledge, chat history, and improvement history locally
- 🔧 **Enhanced Decorator-Based**: Easy integration with existing code using simplified decorators
- 🎯 **A/B Testing**: Compare different prompt variants
- 📝 **Real-time Prompt Editing**: Edit prompts directly in the web interface
- 🎨 **Modern UI**: Beautiful, responsive design with real-time updates

## 🚀 Quick Start

### 1. Add enhanced decorators to your functions

```python
import autopromptix
import openai

# Using the new unified decorator
@autopromptix.test(
    expected_output='./output.txt/@L31',
    test_types=['system_prompt', 'temperature'],
    client='openai',
    max_iterations=5,
    target_score=0.85,
    auto_improve=True,
    prompt_variations=[
        "You are a helpful assistant.",
        "You are a friendly and helpful assistant.",
        "You are a professional assistant."
    ]
)
def greeting():
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"}
        ]
    )
    return response.choices[0].message.content

# Using auto_test for automatic prompt detection
@autopromptix.auto_test
def simple_greeting():
    return "Hello, I'm doing well, thank you for asking!"
```

### 2. Start the Enhanced AutoPromptix server

```python
import autopromptix

# Quick start
autopromptix.quick_start(port=8000)

# Or with custom settings
autopromptix.start_server(
    host='127.0.0.1',
    port=8000,
    api_model='gpt-4o-mini',
    max_test_n=10
)
```

### 3. Access the enhanced web dashboard

Open your browser and navigate to `http://127.0.0.1:8000` to access the enhanced AutoPromptix dashboard.

## 🎯 Enhanced Decorators

### @autopromptix.test
Unified decorator for comprehensive testing:
```python
@autopromptix.test(
    expected_output='./output.txt/@L31',
    test_types=['system_prompt', 'temperature', 'top_k'],
    client='openai',
    max_iterations=10,
    target_score=0.85,
    auto_improve=True,
    prompt_variations=[
        "You are a helpful assistant.",
        "You are a friendly assistant."
    ]
)
```

### @autopromptix.auto_test
Automatic prompt detection and testing:
```python
@autopromptix.auto_test
def my_function():
    # Prompts are automatically detected from source code
    pass
```

### @autopromptix.test_config
Configuration file-based testing:
```python
@autopromptix.test_config('configs/my_function.yaml')
def my_function():
    pass
```

### @autopromptix.prompt_template
Template-based prompt management:
```python
@autopromptix.prompt_template('templates/greeting.yaml')
def greeting():
    pass
```

### autopromptix.test_context
Context manager for test configuration:
```python
with autopromptix.test_context(
    expected_output='./output.txt/@L31',
    test_types=['system_prompt'],
    auto_improve=True
):
    @autopromptix.test
    def my_function():
        pass
```

## 🌐 Enhanced Web Dashboard Features

### Real-time Prompt Editor
- Edit prompts directly in the web interface
- Test prompts instantly
- Save and version control prompts
- Auto-improve prompts with AI

### A/B Testing Interface
- Compare multiple prompt variants
- Visual results comparison
- Statistical analysis
- Winner declaration

### Enhanced Visual Design
- Modern, responsive UI
- Real-time updates
- Beautiful animations
- Mobile-friendly design

## 📁 Configuration Files

### Function Configuration (configs/greeting.yaml)
```yaml
expected_output: './output.txt/@L31'
test_types: ['system_prompt', 'temperature']
client: 'openai'
max_iterations: 5
target_score: 0.85
auto_improve: true
prompt_variations:
  - "You are a helpful assistant."
  - "You are a friendly and helpful assistant."
  - "You are a professional assistant."
```

### Prompt Template (templates/greeting.yaml)
```yaml
name: "Greeting Assistant"
description: "A friendly greeting assistant"
category: "conversation"

base_prompt: |
  You are a helpful assistant.
  Your role is to provide friendly and helpful responses.

variations:
  - name: "Friendly"
    prompt: |
      You are a friendly and helpful assistant.
      Always be warm and welcoming in your responses.
    
  - name: "Professional"
    prompt: |
      You are a professional and helpful assistant.
      Provide clear, concise, and accurate responses.

test_cases:
  - input: "Hello, how are you?"
    expected: "Hello, I'm doing well, thank you for asking! How can I help you today?"
    weight: 1.0
```

## 🔧 API Endpoints

### Enhanced Functions
- `GET /api/functions` - List all registered functions
- `GET /api/functions/{id}` - Get function details
- `POST /api/functions/{id}/test` - Run a single test
- `POST /api/functions/{id}/auto-test` - Run automated tests with improvements
- `GET /api/functions/{id}/prompt-editor` - Get prompt editor interface
- `POST /api/functions/{id}/prompt-editor` - Update prompt
- `POST /api/functions/{id}/ab-test` - Run A/B test between variants

### Prompt Management
- `POST /api/functions/{id}/analyze-prompt` - Analyze a prompt
- `POST /api/functions/{id}/improve-prompt` - Improve a prompt

### Results & Monitoring
- `GET /api/functions/{id}/results` - Get test results
- `GET /api/functions/{id}/improvements` - Get improvement history
- `GET /api/functions/{id}/test-status` - Get test status

### System
- `GET /api/stats` - Get system statistics
- `GET /api/settings` - Get/update settings
- `GET /api/health` - Health check

## 📊 Local Storage

AutoPromptix stores data locally in the `autopromptix_data` directory:

- `knowledge/` - Knowledge base and learned patterns
- `chat_history/` - Chat history and interactions
- `improvements/` - Prompt improvement history
- `autopromptix.db` - SQLite database with test results and metadata

## 🚀 Advanced Usage

### Quick Start Functions
```python
# Quick start with default settings
autopromptix.quick_start(port=8000)

# Start from configuration file
autopromptix.start_from_config('config/autopromptix.yaml')
```

### Manual Test Execution
```python
from autopromptix import test_runner

# Run a single test
result = test_runner.run_single_test(
    function_id='main.greeting',
    test_name='custom_test',
    prompt='You are a friendly assistant.',
    config={'temperature': 0.7}
)

print(f"Test score: {result.score}")
```

### Prompt Analysis
```python
from autopromptix import prompt_improver

# Analyze a prompt
analysis = prompt_improver.analyze_prompt(
    "You are a helpful assistant. Please be concise."
)

print(f"Clarity score: {analysis.clarity_score}")
print(f"Issues: {analysis.potential_issues}")
```

### Automated Improvement
```python
# Improve a prompt automatically
improvement = prompt_improver.improve_prompt(
    function_id='main.greeting',
    original_prompt='You are a helpful assistant.',
    improvement_type='clarity'
)

print(f"Improved prompt: {improvement.improved_prompt}")
print(f"Reason: {improvement.improvement_reason}")
```

## 📋 Requirements

- Python 3.7+
- Flask 2.3.3+
- OpenAI API key (if using OpenAI)
- Modern web browser for dashboard

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/autopromptix/autopromptix/issues
- Documentation: https://autopromptix.readthedocs.io/

## 📝 Changelog

### v0.2.0 (Enhanced)
- ✨ Enhanced decorator system with unified API
- 🎨 Beautiful, modern web dashboard
- 📝 Real-time prompt editing
- 🧪 A/B testing interface
- 🚀 Auto-test decorator for automatic prompt detection
- 📁 Configuration file support
- 🎯 Context manager for test configuration
- 📊 Enhanced visual design and UX
- 🔧 Improved API endpoints
- 📄 License changed to MIT

### v0.1.0
- Initial release
- Basic testing and improvement functionality
- Web dashboard
- Local storage system
- Decorator-based integration 