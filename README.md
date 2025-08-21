# AutoPromptix

AI-Powered Automated Prompt Testing and Optimization Platform

## 🚀 Key Features

- **🤖 AI Prompt Optimization**: Automatically optimize prompts for better results
- **🧪 Automated Testing**: Decorator-based prompt testing framework
- **🔄 Real-time Streaming**: WebSocket support for live optimization progress
- **📊 Smart Evaluation**: Multi-metric scoring with customizable weights
- **🎯 Custom Requirements**: Add specific requirements and exclusions
- **🏗️ Clean Architecture**: Layered design with clear separation of concerns

## 🏗️ Architecture

AutoPromptix follows a clean layered architecture:

```
autopromptix/
├── core/                    # Domain Layer (Business Logic)
│   ├── decorators.py       # Prompt decorators
│   ├── storage.py          # Data storage
│   ├── prompt_improver.py  # Prompt improvement
│   ├── prompt_optimizer.py # AI-powered optimization
│   ├── scorer.py           # Evaluation metrics
│   ├── llm_integration.py  # LLM provider integration
│   └── test_runner.py      # Test execution
├── api/                     # API Layer
│   └── server.py           # Flask + SocketIO API
├── dashboard/               # UI Layer (Web Interface)
│   └── backend/
│       └── server.py       # Dashboard server
└── docker/                  # Deployment
    ├── Dockerfile
    └── docker-compose.yml
```

## 🚀 Quick Start

### Using Python Runner
```bash
# Run full system (API + Dashboard)
python run.py

# Run API only
python run.py --mode api

# Run Dashboard only (requires API running)
python run.py --mode dashboard
```

### Using Docker
```bash
# Build and run with Docker
cd docker
docker-compose up --build

# Access Dashboard: http://localhost:8001
# Access API: http://localhost:8000
```

## 📋 Features

### Core Layer
- **Decorators**: Easy-to-use prompt testing decorators
- **AI Optimization**: Smart prompt mutations based on input analysis
- **Multi-Metric Scoring**: Cosine similarity, ROUGE-L, keyword coverage
- **LLM Integration**: Support for OpenAI, Anthropic, and mock providers
- **Storage**: Persistent data management

### API Layer
- **REST Endpoints**: Full REST API for all functionality
- **WebSocket Support**: Real-time optimization streaming via SocketIO
- **CORS Enabled**: Cross-origin resource sharing support
- **Async Support**: Handles async operations efficiently

### Dashboard Layer
- **Web UI**: Modern web interface
- **Real-time Monitoring**: Live function tracking
- **Test Data Management**: Visual test pool management

## 🔧 Installation

### Prerequisites
- Python 3.7+
- OpenAI API key (optional, for AI features)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
```bash
# Create .env file
OPENAI_API_KEY=your_api_key_here
# or
ANTHROPIC_API_KEY=your_api_key_here
```

## 📖 Usage

### Basic Decorator Usage
```python
from autopromptix.core import autopromptix

@autopromptix(
    role="assistant",
    temperature=0.7,
    max_tokens=100
)
def greeting(message: str) -> str:
    """Generate a friendly greeting response"""
    return f"Hello! {message} How can I help you today?"
```

### Prompt Optimization API
```python
import requests

response = requests.post("http://localhost:8000/api/prompt-optimization/optimize", json={
    "user_input": "Write a project plan",
    "expected_output": "Detailed project plan with timeline and resources",
    "product_name": "ProjectManager",
    "exclude_keywords": ["maybe", "perhaps"],
    "custom_mutators": ["Include specific milestones", "Add risk assessment"]
})

result = response.json()
print(f"Best prompt: {result['best_prompt']}")
print(f"Score: {result['best_score']}")
```

### WebSocket Streaming
```python
import socketio

# Create client
sio = socketio.Client()

@sio.event
def optimization_update(data):
    print(f"{data['type']}: {data['data']['message']}")

# Connect and optimize
sio.connect('http://localhost:8000')
sio.emit('start_optimization', {
    'user_input': 'Create marketing strategy',
    'expected_output': 'Comprehensive marketing plan',
    'product_name': 'Marketing',
    'exclude_keywords': ['impossible']
})
```

## 🌟 API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check
- `GET /api/functions` - List all registered functions
- `GET /api/test-pools` - List test data pools
- `POST /api/test-pools` - Create new test pool
- `GET /api/test-pools/{name}` - Get test pool details
- `DELETE /api/test-pools/{name}` - Delete test pool
- `GET /api/stats` - System statistics

### Optimization Endpoints
- `POST /api/prompt-optimization/optimize` - Optimize a prompt
- `GET /api/prompt-optimization/examples` - Get example scenarios
- `GET /api/prompt-optimization/status` - Check system status

### WebSocket Events
- `connect` - Establish WebSocket connection
- `start_optimization` - Begin streaming optimization
- `stop_optimization` - Stop current optimization
- `optimization_update` - Receive optimization progress
- `optimization_complete` - Optimization finished

## 📊 Optimization Process

1. **Input Analysis**: AI analyzes your request to determine the best approach
2. **Smart Mutations**: Generates targeted prompt variations based on analysis
3. **Multi-Metric Evaluation**: Scores each variation using multiple metrics
4. **Real-time Updates**: Streams progress via WebSocket
5. **Best Result Selection**: Returns the highest-scoring optimized prompt

## 🎯 Evaluation Metrics

- **Cosine Similarity**: Semantic similarity between output and expected result
- **ROUGE-L Score**: Longest common subsequence for sequence matching
- **Keyword Coverage**: Ensures important keywords are included
- **Structure Score**: Evaluates output organization and formatting
- **Custom Criteria**: Apply your own evaluation requirements

## 🐳 Docker

### Development
```bash
docker-compose -f docker/docker-compose.yml up --build
```

### Production
```bash
docker build -f docker/Dockerfile -t autopromptix .
docker run -p 8000:8000 -p 8001:8001 autopromptix
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

Apache License 2.0 - see [LICENSE](LICENSE) for details.