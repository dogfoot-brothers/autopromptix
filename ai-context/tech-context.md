# Technology Context: AutoPromptix

## 🛠️ Core Technology Stack

### Backend Framework
- **Flask 2.3.3**: Web server and API framework
- **Flask-CORS 4.0.0**: Cross-origin resource sharing support
- **Python 3.7+**: Core programming language (supports 3.7-3.11)

### AI/ML Integration
- **OpenAI 1.3.0**: Primary LLM provider for prompt improvement
- **Requests 2.31.0**: HTTP client for API communications

### Data Storage
- **SQLite**: Default embedded database
- **JSON**: Configuration and test data serialization
- **File System**: Local storage for chat history and improvements

### Frontend Technology
- **HTML5 + CSS3**: Core web technologies
- **Google Material Design**: UI component library
- **Vanilla JavaScript**: Client-side functionality
- **Responsive Design**: Mobile-friendly interface

### Development Tools
- **pytest 6.0+**: Testing framework
- **pytest-cov 2.0+**: Coverage reporting
- **black 21.0+**: Code formatting
- **flake8 3.8+**: Linting
- **mypy 0.812+**: Type checking

## 🐳 Containerization

### Docker Setup
- **Base Image**: Python 3.9+ slim
- **Port Exposure**: 8001 (main), 8000 (legacy)
- **Volume Mounts**: `./autopromptix_data` for persistence

### Docker Compose
- **Single Service**: Simplified deployment
- **Environment Variables**: Configuration management
- **Restart Policies**: Automatic recovery

## 📁 Project Structure

```
autopromptix/
├── autopromptix/           # Core Python package
│   ├── decorators.py       # Function decorators
│   ├── test_runner.py      # Test execution engine
│   ├── prompt_improver.py  # AI improvement logic
│   ├── storage.py          # Data persistence
│   └── test_data_pool.py   # Test data management
├── dashboard/
│   └── backend/
│       └── server.py       # Flask web server
├── docker/                 # Docker configuration
├── autopromptix_data/      # Runtime data storage
└── test_data_pools/        # Predefined test datasets
```

## 🔧 Configuration Management

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API authentication
- `AUTOPROMPTIX_HOST`: Server host (default: 0.0.0.0)
- `AUTOPROMPTIX_PORT`: Server port (default: 8001)
- `STORAGE_PATH`: Data directory path

### Configuration Files
- `requirements.txt`: Python dependencies
- `setup.py`: Package metadata and entry points
- `docker-compose.yml`: Container orchestration

## 📊 Data Management

### Storage Locations
- **Database**: `autopromptix_data/autopromptix.db`
- **Chat History**: `autopromptix_data/chat_history/`
- **Improvements**: `autopromptix_data/improvements/`
- **Knowledge Base**: `autopromptix_data/knowledge/`

### Data Formats
- **Test Results**: JSON serialized in SQLite
- **Function Metadata**: Python pickle format
- **Chat Logs**: Plain text with timestamps
- **Improvement Reports**: Markdown format

## 🌐 Network & API

### HTTP Endpoints
- **GET /**: Main dashboard interface
- **GET /api/functions**: List registered functions
- **POST /api/test**: Execute function tests
- **GET /api/results**: Retrieve test results
- **POST /api/improve**: Trigger improvement analysis

### CORS Configuration
- **Allowed Origins**: All origins (development)
- **Allowed Methods**: GET, POST, PUT, DELETE
- **Allowed Headers**: Content-Type, Authorization

## 🔒 Security Considerations

### API Security
- **Input Validation**: All API inputs sanitized
- **Error Handling**: No sensitive data in error responses
- **Rate Limiting**: Future consideration for production

### Data Privacy
- **Local Storage**: All data stored locally by default
- **API Keys**: Environment variable storage
- **Logs**: No sensitive data in application logs

## 🚀 Performance Characteristics

### Resource Requirements
- **Memory**: ~100MB base, scales with test data
- **CPU**: Single-threaded by default, I/O bound
- **Storage**: ~10MB base, grows with test history
- **Network**: Minimal, only for AI API calls

### Optimization Patterns
- **Lazy Loading**: Dashboard loads data on demand
- **Caching**: Function metadata cached in memory
- **Batch Processing**: Multiple tests executed efficiently

## 🔄 Development Workflow

### Local Development
```bash
# Setup
pip install -r requirements.txt
pip install -e .

# Run enhanced server
python enhanced_main.py

# Run tests
pytest autopromptix/
```

### Docker Development
```bash
# Build and run
cd docker
docker build -f Dockerfile.simple -t autopromptix ..
docker run -p 8001:8001 autopromptix
```

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.7 or higher
- **Memory**: 512MB RAM
- **Storage**: 100MB available space
- **Network**: Internet access for AI APIs

### Recommended Requirements
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM
- **Storage**: 1GB available space
- **Network**: Stable broadband connection

## 🔮 Technology Roadmap

### Near-term (Next Release)
- **PostgreSQL Support**: Production database option
- **Redis Caching**: Performance optimization
- **WebSocket Support**: Real-time dashboard updates

### Medium-term
- **Kubernetes Deployment**: Container orchestration
- **Multiple AI Providers**: Beyond OpenAI integration
- **Advanced Analytics**: Time-series data analysis

### Long-term
- **Microservices Architecture**: Component separation
- **GraphQL API**: Flexible data querying
- **Machine Learning**: Automated improvement patterns