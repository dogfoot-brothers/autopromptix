#!/usr/bin/env python3
"""
AutoPromptix Runner

Unified runner for the layered architecture.
"""

import sys
import os
import argparse
import threading
import time

# Add current directory to path
sys.path.append('.')

from api.server import APIServer
from dashboard.backend.server import DashboardServer

def main():
    """Main runner function"""
    parser = argparse.ArgumentParser(description='AutoPromptix Runner')
    parser.add_argument('--mode', choices=['api', 'dashboard', 'full'], 
                       default='full', help='Execution mode')
    parser.add_argument('--api-port', type=int, default=8000, help='API server port')
    parser.add_argument('--dashboard-port', type=int, default=8001, help='Dashboard port')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        run_api_only(args.host, args.api_port)
    elif args.mode == 'dashboard':
        run_dashboard_only(args.host, args.dashboard_port)
    elif args.mode == 'full':
        run_full_system(args.host, args.api_port, args.dashboard_port)

def run_api_only(host, port):
    """Run API server only"""
    print(f"🚀 Starting API server on {host}:{port}")
    
    api_server = APIServer(host=host, port=port)
    api_server.start()
    
    print(f"🌐 API server running at http://{host}:{port}")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping API server...")
        api_server.stop()
        print("✅ API server stopped")

def run_dashboard_only(host, port):
    """Run Dashboard only (requires API server running)"""
    print(f"🚀 Starting Dashboard on {host}:{port}")
    print("⚠️  Make sure API server is running on port 8000")
    
    dashboard = DashboardServer(host=host, port=port, api_url='http://localhost:8000')
    dashboard.start()
    
    print(f"🌐 Dashboard running at http://{host}:{port}")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Dashboard...")
        dashboard.stop()
        print("✅ Dashboard stopped")

def run_full_system(host, api_port, dashboard_port):
    """Run both API and Dashboard"""
    print("🚀 Starting AutoPromptix Full System")
    print("=" * 50)
    
    # Start API server
    api_server = APIServer(host=host, port=api_port)
    api_server.start()
    print(f"✅ API server started on http://{host}:{api_port}")
    
    # Start Dashboard
    dashboard = DashboardServer(host=host, port=dashboard_port, api_url=f'http://localhost:{api_port}')
    dashboard.start()
    print(f"✅ Dashboard started on http://{host}:{dashboard_port}")
    
    print("=" * 50)
    print("🎯 System Features:")
    print("   • Core: Business logic and decorators")
    print("   • API: REST API endpoints")
    print("   • Dashboard: Web UI interface")
    print("🌐 Access Dashboard at: http://localhost:8001")
    print("🌐 Access API at: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping AutoPromptix...")
        api_server.stop()
        dashboard.stop()
        print("✅ AutoPromptix stopped")

if __name__ == "__main__":
    main() 