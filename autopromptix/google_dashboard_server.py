"""
Google-Style AutoPromptix Dashboard Server

Modern Material Design-inspired dashboard with Test Data Pool management.
Now uses separated frontend and backend architecture.
"""

import os
import sys
from pathlib import Path

# Add dashboard backend to path
dashboard_backend_path = os.path.join(os.path.dirname(__file__), '..', 'dashboard', 'backend')
sys.path.insert(0, os.path.abspath(dashboard_backend_path))

from server import DashboardServer

class GoogleStyleDashboardServer:
    """Google Material Design-inspired dashboard server with Test Data Pool management"""
    
    def __init__(self, host='127.0.0.1', port=8001):
        # Delegate to the new separated dashboard server
        self.dashboard_server = DashboardServer(host, port)
    
    @property
    def host(self):
        return self.dashboard_server.host
    
    @property
    def port(self):
        return self.dashboard_server.port
    
    @property
    def app(self):
        return self.dashboard_server.app
    
    @property
    def running(self):
        return self.dashboard_server.running
    
    def start(self):
        """Start the server"""
        return self.dashboard_server.start()
    
    def stop(self):
        """Stop the server"""
        return self.dashboard_server.stop() 