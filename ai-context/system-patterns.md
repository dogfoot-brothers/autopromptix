# System Patterns: AutoPromptix Architecture

## 🏗️ High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │───▶│  Flask Server   │───▶│   Core Engine   │
│  (Dashboard)    │    │   (API Layer)   │    │  (Test Runner)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Test Data Pool │    │  Storage Layer  │
                       │   Management    │    │   (Database)    │
                       └─────────────────┘    └─────────────────┘
```

## 🧩 Core Components

### 1. Decorator Layer (`decorators.py`)
**Pattern**: Decorator Pattern + Registry Pattern
- **Purpose**: Seamless integration with user code
- **Responsibility**: Function wrapping, metadata collection, test registration
- **Key Classes**: `@autopromptix.test`, `@autopromptix.selftest`

### 2. Test Runner (`test_runner.py`)
**Pattern**: Strategy Pattern + Command Pattern
- **Purpose**: Execute tests and coordinate improvement cycles
- **Responsibility**: Test execution, result collection, improvement triggering
- **Key Classes**: `TestRunner`, `TestResult`

### 3. Storage Manager (`storage.py`)
**Pattern**: Repository Pattern + Singleton Pattern
- **Purpose**: Data persistence and retrieval
- **Responsibility**: SQLite database operations, data serialization
- **Key Classes**: `StorageManager`

### 4. Prompt Improver (`prompt_improver.py`)
**Pattern**: Strategy Pattern + Chain of Responsibility
- **Purpose**: AI-powered prompt analysis and improvement
- **Responsibility**: Generate improvement suggestions, analyze patterns
- **Key Classes**: `PromptImprover`

### 5. Dashboard Server (`dashboard/backend/server.py`)
**Pattern**: MVC Pattern + REST API
- **Purpose**: Web interface and API endpoints
- **Responsibility**: HTTP request handling, UI serving, API responses
- **Key Classes**: `DashboardServer`

## 🔧 Design Decisions

### Decorator-First Approach
**Decision**: Use Python decorators as primary integration method
**Rationale**: 
- Minimal code changes required
- Familiar pattern for Python developers
- Non-intrusive to existing applications

### SQLite for Storage
**Decision**: Use SQLite as default storage backend
**Rationale**:
- Zero-configuration setup
- Suitable for development and small-scale deployment
- Easy backup and portability

### Flask for Web Layer
**Decision**: Use Flask instead of FastAPI or Django
**Rationale**:
- Lightweight and simple
- Good ecosystem for dashboard applications
- Easy to containerize

### Material Design UI
**Decision**: Use Google Material Design components
**Rationale**:
- Professional appearance
- Consistent user experience
- Good accessibility support

## 🔄 Data Flow Patterns

### Test Execution Flow
```
User Function Call → Decorator Intercept → Test Runner → Result Storage → Dashboard Update
```

### Improvement Cycle
```
Test Results → Prompt Improver → AI Analysis → Improvement Suggestions → User Review
```

### Dashboard Interaction
```
Web Request → Flask Router → Data Layer → JSON Response → UI Update
```

## 🛡️ Error Handling Patterns

### Graceful Degradation
- Function execution continues even if testing fails
- Dashboard remains functional with partial data
- Storage errors don't break core functionality

### Exception Isolation
- Each test case runs in isolation
- Failed tests don't affect subsequent tests
- Component failures are logged and reported

## 🚀 Scalability Patterns

### Horizontal Scaling (Future)
- Multiple test runner instances
- Distributed storage backends
- Load-balanced dashboard servers

### Vertical Scaling
- Configurable test concurrency
- Efficient database queries
- Memory-conscious data structures

## 🔌 Extension Points

### Custom Storage Backends
- Interface: `StorageManager` base class
- Examples: PostgreSQL, MongoDB, Redis

### Custom Improvement Strategies
- Interface: `PromptImprover` strategy methods
- Examples: Different AI models, custom heuristics

### Custom Test Data Sources
- Interface: `TestDataPool` interface
- Examples: API data sources, file imports, generated data

## 📦 Deployment Patterns

### Docker-First
- Primary deployment method
- Consistent environment across platforms
- Easy scaling and orchestration

### Development Mode
- Direct Python execution
- Hot reloading for development
- Integrated debugging support

### Production Considerations
- Environment variable configuration
- Health check endpoints
- Graceful shutdown handling