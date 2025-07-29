#!/bin/bash
set -e

# AutoPromptix Production Docker Entry Point

echo "🚀 Starting AutoPromptix in production mode..."

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY environment variable is not set"
    echo "   Some features may not work properly"
fi

# Set default values for environment variables
export HOST=${HOST:-"0.0.0.0"}
export PORT=${PORT:-8000}
export API_MODEL=${API_MODEL:-"gpt-4o-mini"}
export MAX_TEST_N=${MAX_TEST_N:-10}
export PROMPT_MODIFY_TEMPERATURE=${PROMPT_MODIFY_TEMPERATURE:-10}

# Create necessary directories
mkdir -p /app/autopromptix_data/chat_history
mkdir -p /app/autopromptix_data/improvements
mkdir -p /app/autopromptix_data/knowledge
mkdir -p /app/test_data_pools

# Function to start the server
start_server() {
    local mode=${1:-"enhanced"}
    
    case $mode in
        "basic")
            echo "📡 Starting basic AutoPromptix server on port $PORT"
            exec python main.py
            ;;
        "enhanced")
            echo "📡 Starting enhanced AutoPromptix server on port $PORT"
            exec python enhanced_main.py
            ;;
        "dashboard")
            echo "📡 Starting dashboard server on port $PORT"
            exec python dashboard/run_dashboard.py
            ;;
        *)
            echo "❌ Unknown mode: $mode"
            echo "Available modes: basic, enhanced, dashboard"
            exit 1
            ;;
    esac
}

# Check if a specific mode is requested
if [ -n "$AUTOPROMPTIX_MODE" ]; then
    start_server "$AUTOPROMPTIX_MODE"
else
    # Default to enhanced mode
    start_server "enhanced"
fi 