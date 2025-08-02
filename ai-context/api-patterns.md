# API Patterns: AutoPromptix Web Interface

## 🌐 REST API Design

### Base URL Structure
```
http://localhost:8001/api/v1/
```

### Authentication
- **Current**: No authentication (development phase)
- **Planned**: JWT-based authentication for production

## 📡 API Endpoints

### Function Management
```http
GET /api/functions
# Returns: List of registered AI functions with metadata

GET /api/functions/{function_id}
# Returns: Detailed function information and test history

POST /api/functions/{function_id}/test
# Body: { "test_cases": [...], "config": {...} }
# Returns: Test execution results
```

### Test Data Pools
```http
GET /api/test-pools
# Returns: Available test data pools

POST /api/test-pools
# Body: TestDataPool object
# Returns: Created pool ID

GET /api/test-pools/{pool_id}/cases
# Returns: Test cases in the specified pool
```

### Results & Analytics
```http
GET /api/results
# Query params: function_id, date_range, limit
# Returns: Paginated test results

GET /api/analytics/summary
# Returns: Performance metrics and trends

POST /api/improve/{function_id}
# Triggers AI-powered improvement analysis
# Returns: Improvement suggestions
```

## 📊 Data Models

### Function Metadata
```json
{
  "id": "string",
  "name": "string",
  "module": "string",
  "description": "string",
  "test_config": {
    "auto_test": true,
    "test_cases": ["..."],
    "expected_output_type": "string"
  },
  "last_tested": "2024-01-01T00:00:00Z",
  "test_count": 42,
  "success_rate": 0.95
}
```

### Test Result
```json
{
  "id": "string",
  "function_id": "string",
  "input_data": "any",
  "output_data": "any",
  "execution_time_ms": 150,
  "success": true,
  "error_message": null,
  "timestamp": "2024-01-01T00:00:00Z",
  "metadata": {}
}
```

### Improvement Suggestion
```json
{
  "id": "string",
  "function_id": "string",
  "type": "prompt_optimization",
  "confidence": 0.85,
  "suggestion": "Consider adding more specific context...",
  "impact_estimate": "medium",
  "implementation_effort": "low",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🔄 Request/Response Patterns

### Standard Response Format
```json
{
  "success": true,
  "data": { /* actual response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "test_cases",
      "issue": "Must be a non-empty array"
    }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Pagination Pattern
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

## 🎯 Frontend Integration Patterns

### Dashboard Data Flow
1. **Initial Load**: Fetch function list and summary stats
2. **Real-time Updates**: Poll for new test results every 5 seconds
3. **User Actions**: Trigger tests and improvements via POST requests
4. **Error Handling**: Display user-friendly error messages

### WebSocket Integration (Planned)
```javascript
// Real-time test result updates
const ws = new WebSocket('ws://localhost:8001/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'test_result') {
    updateDashboard(data.payload);
  }
};
```

## 🔧 API Conventions

### HTTP Status Codes
- **200**: Success with data
- **201**: Resource created
- **400**: Bad request (validation error)
- **404**: Resource not found
- **500**: Internal server error

### URL Naming
- Use kebab-case for URLs: `/test-pools`
- Use plural nouns for collections: `/functions`
- Use meaningful resource identifiers: `/functions/{function_id}`

### Request Headers
```http
Content-Type: application/json
Accept: application/json
X-Request-ID: unique-request-identifier
```

### Query Parameters
- **Filtering**: `?status=active&type=test`
- **Sorting**: `?sort=created_at&order=desc`
- **Pagination**: `?page=1&limit=20`
- **Includes**: `?include=metadata,results`

## 🛡️ Security Patterns

### Input Validation
- Validate all input parameters
- Sanitize string inputs to prevent injection
- Limit request size and complexity
- Rate limiting (planned)

### Error Handling
- Never expose internal details in error messages
- Log security-relevant events
- Return consistent error formats
- Implement proper CORS headers

## 📈 Performance Patterns

### Caching Strategy
- Cache function metadata in memory
- Use ETags for conditional requests
- Implement query result caching
- Background cache warming

### Optimization Techniques
- Lazy loading of large datasets
- Compression for large responses
- Database query optimization
- Connection pooling for external APIs

## 🔮 Future API Evolution

### Versioning Strategy
- URL path versioning: `/api/v2/`
- Backward compatibility for at least 2 versions
- Deprecation notices in response headers
- Migration guides for breaking changes

### Planned Enhancements
- **GraphQL Endpoint**: Flexible data querying
- **Batch Operations**: Multiple operations in single request
- **Webhooks**: Event notifications to external systems
- **OpenAPI Specification**: Full API documentation