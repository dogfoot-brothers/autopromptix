#!/usr/bin/env python3
"""
Development script to run the AutoPromptix Dashboard

This script starts the backend server and provides instructions for the frontend.
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def run_backend():
    """Run the backend server"""
    print("🚀 Starting AutoPromptix Dashboard Backend...")
    
    # Add the backend directory to Python path
    backend_dir = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
    # Import and start the server
    from server import DashboardServer
    
    server = DashboardServer()
    server.start()
    
    print(f"✅ Backend server running on http://{server.host}:{server.port}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Shutting down backend server...")
        server.stop()

def print_frontend_instructions():
    """Print instructions for running the frontend"""
    frontend_dir = Path(__file__).parent / "frontend"
    
    print("\n" + "="*60)
    print("📦 FRONTEND SETUP INSTRUCTIONS")
    print("="*60)
    print(f"1. Open a new terminal")
    print(f"2. Navigate to: {frontend_dir}")
    print(f"3. Install dependencies: npm install")
    print(f"4. Start development server: npm run dev")
    print(f"5. Open browser to: http://localhost:3000")
    print("\n💡 The frontend will automatically proxy API calls to the backend.")
    print("="*60)

def main():
    """Main function"""
    print("🎯 AutoPromptix Dashboard Development Setup")
    print("-" * 50)
    
    # Check if we're in the right directory
    if not (Path(__file__).parent / "backend" / "server.py").exists():
        print("❌ Error: backend/server.py not found!")
        print("Please run this script from the dashboard directory.")
        sys.exit(1)
    
    # Frontend removed - using built-in HTML dashboard
    print("📊 Using built-in HTML dashboard")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    print("\n🔄 Dashboard is now running:")
    print("   Backend:  http://127.0.0.1:8001 (API + Frontend)")
    print("\n Press Ctrl+C to stop the server.")
    
    try:
        # Keep the main thread alive
        backend_thread.join()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main() 