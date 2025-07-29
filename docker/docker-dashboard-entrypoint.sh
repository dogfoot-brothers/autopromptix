#!/bin/bash
set -e

# AutoPromptix Dashboard Docker Entry Point

echo "🎨 Starting AutoPromptix Dashboard..."

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set"
    echo "   Some features may not work properly"
fi

# Set default values for environment variables
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-8001}
export API_MODEL=${API_MODEL:-"gpt-4o-mini"}
export MAX_TEST_N=${MAX_TEST_N:-10}
export PROMPT_MODIFY_TEMPERATURE=${PROMPT_MODIFY_TEMPERATURE:-10}

# Create necessary directories
mkdir -p /app/autopromptix_data/chat_history
mkdir -p /app/autopromptix_data/improvements
mkdir -p /app/autopromptix_data/knowledge
mkdir -p /app/test_data_pools

# Build frontend if not already built
if [ ! -d "/app/dashboard/frontend/dist" ]; then
    echo "🔨 Building frontend..."
    cd /app/dashboard/frontend
    npm install
    npm run build
    cd /app
fi

# Start the dashboard server
echo "📡 Starting dashboard server on port $PORT"
echo "🌐 Dashboard will be available at http://localhost:$PORT"

exec python dashboard/run_dashboard.py 