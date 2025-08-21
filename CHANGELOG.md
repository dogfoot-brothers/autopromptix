# Changelog

All notable changes to AutoPromptix are documented in this file.

## [1.0.0] - 2024

### 🎉 Major Release - AI-Powered Prompt Optimization

This release transforms AutoPromptix into a comprehensive AI-powered prompt optimization platform, combining the original decorator-based testing framework with advanced optimization capabilities.

### ✨ New Features

#### AI-Powered Optimization
- **Smart Mutation Generation**: AI analyzes user input and generates targeted prompt variations
- **Multi-Metric Evaluation**: Comprehensive scoring using:
  - Cosine similarity for semantic matching
  - ROUGE-L for sequence alignment
  - Keyword coverage analysis
  - Structure quality assessment
  - Custom criteria evaluation
- **Customizable Evaluation Weights**: Fine-tune how prompts are scored
- **Exclude Keywords**: Prevent specific words from appearing in outputs
- **Custom Requirements**: Add specific instructions for optimization

#### Real-time Streaming
- **WebSocket Support**: Live optimization progress via SocketIO
- **Streaming Updates**: Real-time feedback on:
  - Analysis progress
  - Mutation generation
  - Evaluation scores
  - Final results
- **Session Management**: Handle multiple concurrent optimizations

#### LLM Integration
- **Multi-Provider Support**:
  - OpenAI (GPT models)
  - Anthropic (Claude models)
  - Mock provider for testing
- **Async Operations**: Efficient handling of LLM calls
- **Environment Configuration**: Simple `.env` setup

#### Enhanced API
- **Unified Design**: Single API combining all features
- **REST Endpoints**: Full REST API for all operations
- **WebSocket Events**: Real-time bidirectional communication
- **Better Error Handling**: Detailed error messages and validation

### 📊 API Endpoints

#### New Optimization Endpoints
- `POST /api/prompt-optimization/optimize` - AI-powered prompt optimization
- `GET /api/prompt-optimization/examples` - Example optimization scenarios
- `GET /api/prompt-optimization/status` - System status check

#### WebSocket Events
- `start_optimization` - Begin streaming optimization
- `stop_optimization` - Cancel current optimization
- `optimization_update` - Receive progress updates
- `optimization_complete` - Optimization finished

### 🔧 Technical Improvements

- **Async Architecture**: Better performance with async/await
- **Modular Design**: Clean separation of concerns
- **Extensible Scoring**: Easy to add new evaluation metrics
- **Flexible Configuration**: Customizable weights and parameters
- **Type Hints**: Improved code clarity and IDE support

### 📦 Dependencies

#### New Dependencies
- `flask-socketio` - WebSocket support for Flask
- `python-socketio` - SocketIO client/server
- `rapidfuzz` - Fast string matching
- `rouge-score` - ROUGE metric calculation

### 🐛 Bug Fixes
- Improved error handling in decorator system
- Better Unicode support for international text
- Fixed memory leaks in long-running sessions
- Enhanced stability for concurrent requests

### 📚 Documentation
- Comprehensive README with examples
- Feature guide for new capabilities
- API documentation for all endpoints
- Example code demonstrating usage

### 🔄 Migration
- No breaking changes to existing decorator API
- Original functionality fully preserved
- New features are opt-in
- Smooth upgrade path

## [0.1.0] - Previous Version

### Initial Features
- Decorator-based prompt testing
- Test data pool management
- Basic prompt improvement
- Flask REST API
- Web dashboard

---

For more details, see the [README](README.md) and [Feature Guide](MIGRATION_GUIDE.md).
