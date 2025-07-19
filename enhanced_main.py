import autopromptix
import openai
import os

# Set OpenAI API key (you should set this in your environment)
# os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Enhanced AutoPromptix settings
autopromptix_settings = {
    'host': '127.0.0.1',
    'port': 8001,  # Changed from 8000 to 8001
    'api_model': 'gpt-4o-mini',
    'max_test_n': 10,
    'prompt_modify_temperature': 10
}

# Using the new enhanced decorator
@autopromptix.test(
    expected_output='./output.txt/@L31',
    test_types=['system_prompt', 'temperature'],
    client='openai',
    max_iterations=5,
    target_score=0.85,
    auto_improve=True,
    prompt_variations=[
        "You are a helpful assistant.",
        "You are a friendly and helpful assistant.",
        "You are a professional assistant.",
        "You are a knowledgeable and helpful assistant."
    ]
)
def greeting():
    """A simple greeting function that uses OpenAI API"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Example with auto_test decorator
@autopromptix.auto_test
def simple_greeting():
    """Simple greeting without OpenAI API"""
    return "Hello, I'm doing well, thank you for asking! How can I help you today?"

def main():
    """Main function to start Enhanced AutoPromptix and run the greeting function"""
    print("🚀 Starting Enhanced AutoPromptix...")
    
    # Start the Enhanced AutoPromptix server
    from autopromptix.enhanced_server import EnhancedAutoPromptixServer
    
    server = EnhancedAutoPromptixServer(
        host=autopromptix_settings['host'],
        port=autopromptix_settings['port'],
        api_model=autopromptix_settings['api_model'],
        max_test_n=autopromptix_settings['max_test_n'],
        prompt_modify_temperature=autopromptix_settings['prompt_modify_temperature']
    )
    
    server.start()
    
    print(f"✨ Enhanced AutoPromptix server started at http://{autopromptix_settings['host']}:{autopromptix_settings['port']}")
    print("🌐 Access the enhanced dashboard in your web browser!")
    print("📝 Features:")
    print("   - Real-time prompt editing")
    print("   - A/B testing interface")
    print("   - Enhanced visual design")
    print("   - Improved usability")
    
    # Run the greeting function to register it
    print("\n🧪 Running greeting function...")
    result = greeting()
    print(f"Greeting result: {result}")
    
    # Run simple greeting
    print("\n🧪 Running simple greeting...")
    simple_result = simple_greeting()
    print(f"Simple greeting result: {simple_result}")
    
    # The server will keep running in the background
    print("\n🔄 Server is running. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Enhanced AutoPromptix server...")
        server.stop()
        print("✅ Server stopped.")

if __name__ == "__main__":
    main() 