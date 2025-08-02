# AutoPromptix Dashboard

A modern, Google-like dashboard for the AutoPromptix AI function testing and improvement framework.

## Architecture

The dashboard is split into two separate applications:

- **Backend**: Flask API server (`backend/server.py`)
- **Frontend**: Vite + React + TypeScript + Material-UI (`frontend/`)

## Quick Start

### 1. Start the Backend API Server

```bash
cd dashboard/backend
python server.py
```

The API server will run on `http://localhost:8001`

### 2. Start the Frontend Development Server

```bash
cd dashboard/frontend
yarn install
yarn dev
```

The frontend will run on `http://localhost:3000` with API proxy configured.

## Features

### Backend API
- **RESTful API** for AutoPromptix functionality
- **Function Management** - View registered AI functions
- **Test Pool Management** - Create, view, delete test data pools
- **Statistics** - System metrics and health monitoring
- **CORS enabled** for frontend integration

### Frontend Dashboard
- **Modern UI** with Material-UI components
- **Responsive Design** that works on desktop and mobile
- **Google-like Interface** with clean sidebar navigation
- **Real-time Data** fetched from the backend API
- **Interactive Components** for managing test pools and functions

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/api/stats` | System statistics |
| GET | `/api/functions` | List registered functions |
| GET | `/api/test-pools` | List test pools |
| GET | `/api/test-pools/<name>` | Get pool details |
| POST | `/api/test-pools` | Create new test pool |
| DELETE | `/api/test-pools/<name>` | Delete test pool |

## Development

### Frontend Stack
- **Vite** - Fast build tool and dev server
- **React 18** - UI library
- **TypeScript** - Type safety
- **Material-UI** - Google Material Design components
- **Yarn Berry** - Package manager
- **Axios** - HTTP client

### Backend Stack
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **AutoPromptix** - Core AI testing framework

## Configuration

### Frontend (vite.config.ts)
```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true,
    },
  },
}
```

### Backend (server.py)
```python
server = DashboardServer(host='127.0.0.1', port=8001)
```

## Building for Production

### Frontend
```bash
cd frontend
yarn build
```

Builds the app for production to the `dist/` folder.

### Backend
The Flask backend can be deployed using any WSGI server:

```python
from dashboard.backend.server import create_app
app = create_app()
```

## Troubleshooting

### Port Conflicts
- Backend default: `:8001`
- Frontend default: `:3000`
- Change ports in configuration files if needed

### CORS Issues
- Backend has CORS enabled for all origins in development
- Adjust CORS settings for production deployment

### API Connection
- Ensure backend is running before starting frontend
- Check proxy configuration in `vite.config.ts`