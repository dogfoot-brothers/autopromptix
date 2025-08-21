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
COPY run.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash autopromptix && \
    chown -R autopromptix:autopromptix /app
USER autopromptix

# Expose ports
EXPOSE 8000 8001

# Default command - use the run.py script
CMD ["python", "run.py", "--host", "0.0.0.0"] 