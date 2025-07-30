#!/usr/bin/env python3
"""
Enhanced AutoPromptix Main Script with Simplified Test Data Pool Dashboard

This script demonstrates the enhanced AutoPromptix system with:
- Google Material Design dashboard
- Test Data Pool integration
- User-friendly interface with tooltips
"""

import sys
import os
from autopromptix.decorators import autopromptix
from autopromptix.test_data_pool import create_greeting_test_pool, TestDataPoolManager

# Add dashboard backend to path
dashboard_backend = os.path.join(os.path.dirname(__file__), 'dashboard', 'backend')
sys.path.insert(0, dashboard_backend)

from server import DashboardServer

def main():
    """Main function to run the enhanced AutoPromptix system"""
    
    print("🚀 Starting Enhanced AutoPromptix with Test Data Pool Dashboard")
    print("=" * 60)
    
    # Create sample test data pool
    print("📦 Creating sample test data pool...")
    greeting_pool = create_greeting_test_pool()
    test_data_manager = TestDataPoolManager()
    test_data_manager.create_pool(greeting_pool)
    
    # Initialize dashboard server
    dashboard = DashboardServer(
        host='0.0.0.0',  # Allow external access
        port=8001
    )
    
    print(f"🚀 Dashboard Server running on http://{dashboard.host}:{dashboard.port}")
    
    print("🎨 Features:")
    print("   • Material Design UI")
    print("   • Test Data Pool management")
    print("   • Interactive tooltips")
    print("   • Real-time function monitoring")
    
    # Run sample tests
    print("🧪 Running sample tests...")
    
    print("1. Testing greeting function:")
    result1 = greeting("Hello, how are you?")
    print(f"   Input: Hello, how are you?")
    print(f"   Output: {result1[:50]}...")
    
    print("2. Testing greeting with different input:")
    result2 = greeting("Good morning!")
    print(f"   Input: Good morning!")
    print(f"   Output: {result2[:50]}...")
    
    # Display registered functions
    print("📋 Registered Functions:")
    print("   • greeting() - 인사 함수")
    print("     - Test Data Pool: greeting_test_cases")
    print("     - Hover for details in dashboard")
    
    print("=" * 60)
    print("🎯 Dashboard Features:")
    print("   • View functions with hover tooltips")
    print("   • Manage Test Data Pools")
    print("   • Create and edit test cases")
    print("   • Real-time monitoring")
    print("🌐 Open your browser and go to: http://127.0.0.1:8001")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        # Start the dashboard server
        dashboard.start()
        
        # Keep the server running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            dashboard.stop()
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

# Essential greeting function with autopromptix decorator and test data pool
@autopromptix(
    role="assistant",
    temperature=0.7,
    max_tokens=100,
    test_data_pool="greeting"  # Connect to test data pool
)
def greeting(message: str) -> str:
    """
    Generate a friendly greeting response.
    
    Args:
        message: The input message from the user
        
    Returns:
        A friendly greeting response
    """
    if not message or message.strip() == "":
        return "Hello! I didn't catch that. Could you please say something?"
    
    return f"Hello! I received your message: '{message}'. How can I help you today?"

if __name__ == "__main__":
    main() 