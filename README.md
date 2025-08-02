# AutoPromptix

Automated Prompt Testing and Improvement Tool with Layered Architecture

## 🏗️ Architecture

AutoPromptix follows a clean layered architecture:

```
autopromptix/
├── core/                    # Domain Layer (Business Logic)
│   ├── decorators.py       # Prompt decorators
│   ├── storage.py          # Data storage
│   ├── prompt_improver.py  # Prompt improvement
│   └── test_runner.py      # Test execution
├── api/                     # Presentation Layer (REST API)
│   └── server.py           # API endpoints
├── dashboard/               # UI Layer (Web Interface)
│   └── backend/
│       └── server.py       # Web UI server
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
- **Storage**: Persistent data management
- **Prompt Improvement**: Automated prompt optimization
- **Test Runner**: Comprehensive test execution

### API Layer
- **REST API**: Full REST API for core functionality
- **JSON Responses**: Structured data exchange
- **CORS Support**: Cross-origin resource sharing

### Dashboard Layer
- **Web UI**: Modern web interface
- **Real-time Monitoring**: Live function tracking
- **Test Data Management**: Visual test pool management

## 🔧 Development

### Prerequisites
- Python 3.7+
- Docker (optional)

### Installation
```bash
pip install -r requirements.txt
```

### Running Tests
```bash
# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest
```

## 📖 Usage

### Basic Decorator Usage
```python
from core import autopromptix

@autopromptix(
    role="assistant",
    temperature=0.7,
    max_tokens=100
)
def greeting(message: str) -> str:
    """Generate a friendly greeting response"""
    return f"Hello! {message} How can I help you today?"
```

### API Endpoints
- `GET /api/functions` - List all registered functions
- `GET /api/test-pools` - List test data pools
- `POST /api/test-pools` - Create new test pool
- `GET /api/stats` - System statistics

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

## 📝 License

Apache License 2.0 - see [LICENSE](LICENSE) for details. 