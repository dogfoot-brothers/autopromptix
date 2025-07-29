# AutoPromptix Docker Image
# Multi-stage build for different deployment scenarios

# Base Python image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

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

# Copy application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create non-root user
RUN useradd --create-home --shell /bin/bash autopromptix && \
    chown -R autopromptix:autopromptix /app
USER autopromptix

# Expose ports
EXPOSE 8000 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/stats || exit 1

# Default command
CMD ["python", "enhanced_main.py"]

# =============================================================================
# Development stage
# =============================================================================
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy

# Set development environment
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

# =============================================================================
# Production stage
# =============================================================================
FROM base as production

# Set production environment
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Use gunicorn for production
RUN pip install --no-cache-dir gunicorn

# Create production entry point
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

# =============================================================================
# Dashboard stage (with frontend)
# =============================================================================
FROM base as dashboard

# Install Node.js for frontend build
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Copy frontend files
COPY dashboard/frontend/package*.json ./dashboard/frontend/

# Install frontend dependencies
WORKDIR /app/dashboard/frontend
RUN npm ci --only=production

# Build frontend
COPY dashboard/frontend/ ./dashboard/frontend/
RUN npm run build

# Switch back to app directory
WORKDIR /app

# Create dashboard entry point
COPY docker-dashboard-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-dashboard-entrypoint.sh

ENTRYPOINT ["docker-dashboard-entrypoint.sh"] 