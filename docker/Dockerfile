# Optimized AutoPromptix Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy core library
COPY core/ ./core/

# Copy API server
COPY api/ ./api/

# Copy dashboard backend
COPY dashboard/backend/ ./dashboard/backend/

# Copy test data pools
COPY test_data_pools/ ./test_data_pools/

# Copy setup files
COPY setup.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash autopromptix && \
    chown -R autopromptix:autopromptix /app
USER autopromptix

# Expose ports
EXPOSE 8000 8001

# Default command - start both API and Dashboard
CMD ["python", "-c", "import sys; sys.path.append('.'); from api.server import APIServer; from dashboard.backend.server import DashboardServer; import threading; import time; api = APIServer(host='0.0.0.0', port=8000); dashboard = DashboardServer(host='0.0.0.0', port=8001, api_url='http://localhost:8000'); api.start(); dashboard.start(); print('🚀 AutoPromptix running on ports 8000 (API) and 8001 (Dashboard)'); [time.sleep(1) for _ in iter(int, 1)]"] 