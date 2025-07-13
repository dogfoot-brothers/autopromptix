import autopromptix
import openai
import os

# Set OpenAI API key (you should set this in your environment)
# os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Set auto promptix client
autopromptix_settings = {}

autopromptix_settings['host'] = '127.0.0.1'
autopromptix_settings['port'] = 8000
autopromptix_settings['api_model'] = 'gpt-4o-mini'  # default = opensource llm(lama, qwen)
autopromptix_settings['max_test_n'] = 10  # default = 10
autopromptix_settings['prompt_modify_temperature'] = 10  # default = 10

@autopromptix.selftest
@autopromptix.desiredoutput('./output.txt/@L31')
@autopromptix.self_test_system_prompt
@autopromptix.self_test_temperature
@autopromptix.self_test_k
@autopromptix.client('openai')
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

def main():
    """Main function to start AutoPromptix and run the greeting function"""
    print("Starting AutoPromptix...")
    
    # Start the AutoPromptix server
    autopromptix.start_server(
        host=autopromptix_settings['host'],
        port=autopromptix_settings['port'],
        api_model=autopromptix_settings['api_model'],
        max_test_n=autopromptix_settings['max_test_n'],
        prompt_modify_temperature=autopromptix_settings['prompt_modify_temperature']
    )
    
    print(f"AutoPromptix server started at http://{autopromptix_settings['host']}:{autopromptix_settings['port']}")
    print("Access the dashboard in your web browser!")
    
    # Run the greeting function to register it
    print("\nRunning greeting function...")
    result = greeting()
    print(f"Greeting result: {result}")
    
    # The server will keep running in the background
    print("\nServer is running. Press Ctrl+C to stop.")
    
    try:
        # Keep the main thread alive
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping AutoPromptix server...")
        autopromptix.stop_server()
        print("Server stopped.")

if __name__ == "__main__":
    main()