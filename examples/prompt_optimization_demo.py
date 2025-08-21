"""
AutoPromptix Prompt Optimization Demo

This example demonstrates the AI-powered prompt optimization features
using the unified API with both REST and WebSocket endpoints.
"""

import asyncio
import aiohttp
import json
import socketio
from typing import Dict, Any

# API endpoint
API_BASE_URL = "http://localhost:8000"

async def optimize_prompt_example():
    """Example of using the prompt optimization API"""
    
    # Example 1: Customer Service Email
    print("=== Example 1: Customer Service Email ===")
    
    optimization_request = {
        "user_input": "Write an apology email to customer",
        "expected_output": "Professional apology email with reason, solution, and prevention measures",
        "product_name": "CustomerService",
        "exclude_keywords": ["never", "impossible", "cannot"],
        "custom_mutators": [
            "Use empathetic and professional tone",
            "Include specific timeline and action items"
        ],
        "evaluation_weights": {
            "exclude_keywords": 30,
            "product_name": 20,
            "expected_output": 30,
            "custom_requirements": 20
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/api/prompt-optimization/optimize",
            json=optimization_request
        ) as response:
            result = await response.json()
            
            print(f"Original request: {optimization_request['user_input']}")
            print(f"Best score: {result['best_score']}")
            print(f"Best variant: {result['best_variant']}")
            print(f"Score improvement: {result['score_improvement']}")
            print(f"\nOptimized prompt:\n{result['best_prompt']}")
            print(f"\nBest output:\n{result['best_output'][:200]}...")
            print("\n" + "="*50 + "\n")

async def socketio_streaming_example():
    """Example of using SocketIO for real-time optimization"""
    
    print("=== SocketIO Streaming Example ===")
    
    # Create SocketIO client
    sio = socketio.AsyncClient()
    
    # Event handlers
    @sio.event
    async def connect():
        print("Connected to AutoPromptix WebSocket")
    
    @sio.event
    async def disconnect():
        print("Disconnected from WebSocket")
    
    @sio.event
    async def connected(data):
        print(f"Server: {data['message']}")
    
    @sio.event
    async def optimization_update(data):
        """Handle optimization updates"""
        update_type = data['type']
        update_data = data['data']
        
        if update_type == 'status':
            print(f"Status: {update_data['message']}")
        elif update_type == 'analysis':
            print(f"Analysis: {update_data['analysis']['direction']}")
        elif update_type == 'mutations':
            print(f"Generated {len(update_data['mutations'])} variations")
        elif update_type == 'evaluation_start':
            print(f"Evaluating: {update_data['name']} ({update_data['index']+1}/{update_data['total']})")
        elif update_type == 'evaluation_result':
            print(f"  Score: {update_data['trial']['score']:.3f}")
        elif update_type == 'final_results':
            print(f"\nOptimization Complete!")
            print(f"Best score: {update_data['best_score']}")
            print(f"Best variant: {update_data['best_variant']}")
            print(f"Improvement: {update_data['score_improvement']}")
    
    @sio.event
    async def optimization_complete(data):
        print(f"Complete: {data['message']}")
        await sio.disconnect()
    
    @sio.event
    async def optimization_error(data):
        print(f"Error: {data['error']}")
        await sio.disconnect()
    
    try:
        # Connect to server
        await sio.connect(f"{API_BASE_URL}")
        
        # Send optimization request
        optimization_request = {
            "user_input": "Create a marketing strategy",
            "expected_output": "Comprehensive marketing plan with target audience, channels, budget, and KPIs",
            "product_name": "MarketingPro",
            "exclude_keywords": ["maybe", "perhaps", "might"],
            "custom_mutators": [
                "Include specific metrics and KPIs",
                "Add budget allocation details"
            ]
        }
        
        await sio.emit('start_optimization', optimization_request)
        print("Sent optimization request via SocketIO")
        
        # Wait for completion
        await sio.wait()
        
    except Exception as e:
        print(f"SocketIO error: {e}")
    finally:
        if sio.connected:
            await sio.disconnect()

async def test_decorator_example():
    """Example of using the AutoPromptix decorator"""
    
    print("=== Decorator Example ===")
    
    # This would normally be in your code
    from autopromptix.core import autopromptix
    
    @autopromptix(
        role="marketing assistant",
        temperature=0.8,
        max_tokens=200,
        test_data_pool="marketing_examples"
    )
    async def generate_product_description(product_name: str, features: list) -> str:
        """Generate compelling product descriptions"""
        # The decorator handles prompt optimization automatically
        prompt = f"Create a compelling product description for {product_name} with features: {', '.join(features)}"
        
        # In real usage, this would call the LLM
        # For demo, we'll just return a placeholder
        return f"Introducing {product_name} - A revolutionary product with {len(features)} amazing features!"
    
    # Use the decorated function
    result = await generate_product_description(
        "SmartHome Hub",
        ["Voice control", "Energy monitoring", "Security integration"]
    )
    print(f"Generated description: {result}")

async def test_multiple_examples():
    """Test multiple optimization scenarios"""
    
    print("=== Multiple Examples ===")
    
    examples = [
        {
            "title": "Project Plan",
            "user_input": "Create project plan",
            "expected_output": "Detailed project plan with milestones, resources, and timeline",
            "product_name": "ProjectManager",
            "exclude_keywords": ["maybe", "perhaps"]
        },
        {
            "title": "API Documentation",
            "user_input": "Write API docs",
            "expected_output": "Developer-friendly documentation with examples and authentication details",
            "product_name": "DevDocs",
            "exclude_keywords": ["complex", "difficult"]
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for example in examples:
            print(f"\n--- {example['title']} ---")
            
            async with session.post(
                f"{API_BASE_URL}/api/prompt-optimization/optimize",
                json=example
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Score: {result['best_score']}")
                    print(f"Variant: {result['best_variant']}")
                else:
                    print(f"Error: {response.status}")

async def main():
    """Run all examples"""
    print("AutoPromptix Demo - AI-Powered Prompt Optimization\n")
    
    # Make sure the API server is running
    print("Note: Make sure the API server is running (python run.py --mode api)\n")
    
    try:
        # Check if API is accessible
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status != 200:
                    raise Exception("API server not responding")
        
        # Run examples
        await optimize_prompt_example()
        await socketio_streaming_example()
        await test_decorator_example()
        await test_multiple_examples()
        
    except aiohttp.ClientConnectorError:
        print("Error: Could not connect to API server.")
        print("Please start the server with: python run.py --mode api")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Install required packages for the demo if needed
    try:
        import socketio
    except ImportError:
        print("Installing python-socketio[asyncio_client] for the demo...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-socketio[asyncio_client]"])
    
    asyncio.run(main())