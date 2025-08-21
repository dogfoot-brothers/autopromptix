# AutoPromptix Feature Guide

This guide introduces the new AI-powered features added to AutoPromptix.

## 🆕 What's New

### AI-Powered Prompt Optimization
- **Smart Mutations**: AI analyzes your input and generates targeted prompt variations
- **Multi-Metric Evaluation**: Comprehensive scoring using cosine similarity, ROUGE-L, and custom criteria
- **Real-time Streaming**: WebSocket support for live optimization progress
- **LLM Integration**: Support for OpenAI, Anthropic, and mock providers

### Enhanced API
- **Unified Design**: Single API combining all features
- **WebSocket Support**: Real-time bidirectional communication via SocketIO
- **Async Operations**: Efficient handling of AI operations
- **Better Error Handling**: Detailed error messages and validation

## 🔄 Setup Instructions

### 1. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
```

Key new dependencies:
- `flask-socketio` for WebSocket support
- `python-socketio` for client connections
- `rapidfuzz` and `rouge-score` for evaluation metrics

### 2. Environment Setup

Create a `.env` file for LLM providers:

```bash
# For OpenAI
OPENAI_API_KEY=your_api_key_here

# For Anthropic
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Running AutoPromptix

```bash
# Run full system
python run.py

# Run API only
python run.py --mode api

# Run Dashboard only
python run.py --mode dashboard
```

## 📚 Using the New Features

### AI Prompt Optimization

```python
import requests

# Optimize a prompt using AI
response = requests.post("http://localhost:8000/api/prompt-optimization/optimize", json={
    "user_input": "Write a marketing email",
    "expected_output": "Professional email with clear CTA",
    "product_name": "ProductName",
    "exclude_keywords": ["discount", "free"],
    "custom_mutators": ["Include urgency", "Professional tone"]
})

result = response.json()
print(f"Optimized prompt: {result['best_prompt']}")
print(f"Score: {result['best_score']}")
print(f"Improvement: {result['score_improvement']}")
```

### Real-time Streaming with WebSocket

```python
import socketio

# Create SocketIO client
sio = socketio.Client()

@sio.event
def optimization_update(data):
    """Handle real-time updates"""
    update_type = data['type']
    if update_type == 'status':
        print(f"Status: {data['data']['message']}")
    elif update_type == 'evaluation_result':
        print(f"Score: {data['data']['trial']['score']}")
    elif update_type == 'final_results':
        print(f"Best result: {data['data']['best_score']}")

# Connect and start optimization
sio.connect('http://localhost:8000')
sio.emit('start_optimization', {
    "user_input": "Create project plan",
    "expected_output": "Detailed plan with timeline",
    "product_name": "ProjectManager"
})
```

### Custom Evaluation Weights

```python
# Customize how prompts are evaluated
evaluation_weights = {
    "exclude_keywords": 30,    # Weight for keyword exclusion
    "product_name": 25,        # Weight for product name inclusion
    "expected_output": 25,     # Weight for output matching
    "custom_requirements": 20  # Weight for custom requirements
}

response = requests.post("http://localhost:8000/api/prompt-optimization/optimize", json={
    "user_input": "Write documentation",
    "expected_output": "Clear technical documentation",
    "evaluation_weights": evaluation_weights
})
```

## 🚀 New Features to Explore

### 1. Smart Mutation Types
The AI analyzes your input and chooses the best approach:
- **Structure**: For documents, plans, reports
- **Expertise**: For technical content
- **Specificity**: For detailed, numeric content
- **Persuasiveness**: For marketing, sales
- **Actionability**: For executable plans

### 2. Mock Provider for Testing
Test without API keys:
```python
from autopromptix.core.llm_integration import set_provider, MockProvider
set_provider(MockProvider())
```

### 3. Async Operations
All AI operations run asynchronously for better performance:
```python
from autopromptix.core.prompt_optimizer import optimize_prompt_simple

# This runs asynchronously internally
result = await optimize_prompt_simple(
    user_input="Create a proposal",
    expected_output="Professional business proposal",
    product_name="BusinessPro"
)
```

## 📊 Understanding the Results

### Optimization Results Include:
- `best_prompt`: The optimized prompt text
- `best_output`: Sample output from the best prompt
- `best_score`: Score (0-1) of the best result
- `best_variant`: Which mutation strategy worked best
- `score_improvement`: How much the score improved
- `all_trials`: Details of all variations tested

### Score Components:
- **Cosine Similarity**: How semantically similar the output is to expected
- **ROUGE-L**: Sequence matching score
- **Keyword Coverage**: How well keywords are included
- **Structure Score**: Output organization quality
- **Forbidden Penalty**: Deduction for excluded keywords

## ❓ Troubleshooting

### Issue: Import errors
**Solution**: Install all dependencies with `pip install -r requirements.txt`

### Issue: API key not found
**Solution**: Create `.env` file with your API keys or use mock provider

### Issue: WebSocket connection fails
**Solution**: Ensure the API server is running (`python run.py --mode api`)

### Issue: Low optimization scores
**Solution**: 
- Provide more specific `expected_output`
- Add relevant `custom_mutators`
- Adjust `evaluation_weights` to prioritize what matters

## 🤝 Getting Help

If you encounter issues:
1. Check the examples in `examples/prompt_optimization_demo.py`
2. Review the API response for error messages
3. Enable debug logging for more details
4. Open an issue on GitHub

Happy optimizing! 🚀