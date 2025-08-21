"""
AutoPromptix Unified Example

Shows how the traditional decorator system works together with 
the new AI-powered optimization features.
"""

import asyncio
import requests
from autopromptix.core import autopromptix, test_data_manager, TestDataPool

# Example 1: Traditional decorator usage
@autopromptix(
    role="helpful assistant",
    temperature=0.7,
    max_tokens=150
)
def generate_greeting(name: str, context: str = "general") -> str:
    """Generate a personalized greeting"""
    # In real usage, this would use the LLM
    # For demo, we return a placeholder
    return f"Hello {name}! Welcome to our {context} service."

# Example 2: Using test data pools
def setup_test_pool():
    """Create a test data pool for greetings"""
    pool = TestDataPool(
        name="greeting_examples",
        description="Test cases for greeting generation",
        category="greetings"
    )
    
    pool.add_test_case(
        input_data="John, customer support",
        expected_output="Professional and friendly greeting for support",
        description="Customer support greeting"
    )
    
    pool.add_test_case(
        input_data="Sarah, sales",
        expected_output="Enthusiastic greeting for sales context",
        description="Sales greeting"
    )
    
    test_data_manager.create_pool(pool)
    print("✅ Created test data pool: greeting_examples")

# Example 3: AI-powered optimization
def optimize_greeting_prompt():
    """Use AI to optimize a greeting prompt"""
    
    optimization_request = {
        "user_input": "Create a welcome message for new users",
        "expected_output": "Warm, informative welcome that explains key features and next steps",
        "product_name": "AutoPromptix",
        "exclude_keywords": ["complicated", "difficult", "confusing"],
        "custom_mutators": [
            "Include 3 key benefits",
            "Add clear call-to-action",
            "Keep it under 100 words"
        ],
        "evaluation_weights": {
            "exclude_keywords": 20,
            "product_name": 30,
            "expected_output": 30,
            "custom_requirements": 20
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/prompt-optimization/optimize",
            json=optimization_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n🎯 Optimization Results:")
            print(f"Score: {result['best_score']}")
            print(f"Best variant: {result['best_variant']}")
            print(f"Improvement: {result['score_improvement']}")
            print(f"\nOptimized prompt:\n{result['best_prompt']}")
            print(f"\nSample output:\n{result['best_output']}")
            
            # Show all variations tested
            print("\n📊 All variations tested:")
            for trial in result['all_trials']:
                print(f"  - {trial['name']}: {trial['score']:.3f}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure it's running: python run.py --mode api")

# Example 4: Combining decorator with optimization
@autopromptix(
    role="marketing specialist",
    temperature=0.8,
    test_data_pool="marketing_examples"
)
async def create_marketing_copy(product: str, target_audience: str) -> str:
    """Create marketing copy using optimized prompts"""
    
    # First, optimize the prompt for this specific use case
    optimization = {
        "user_input": f"Write marketing copy for {product} targeting {target_audience}",
        "expected_output": "Compelling marketing copy with benefits, features, and CTA",
        "product_name": product,
        "exclude_keywords": ["maybe", "perhaps", "might"],
        "custom_mutators": [
            "Focus on benefits over features",
            "Include social proof",
            "Create urgency"
        ]
    }
    
    try:
        # This would normally call the optimization API
        # For demo, we'll simulate the result
        optimized_prompt = f"""
Create compelling marketing copy for {product} that:
1. Highlights key benefits for {target_audience}
2. Includes social proof and testimonials
3. Creates urgency with limited-time offers
4. Ends with clear call-to-action

Make it persuasive, benefit-focused, and under 150 words.
"""
        
        # In real usage, this would use the optimized prompt with LLM
        return f"Optimized marketing copy for {product} targeting {target_audience}"
        
    except Exception as e:
        return f"Error: {e}"

def main():
    """Run all examples"""
    print("AutoPromptix Unified Example\n")
    print("="*50)
    
    # Traditional decorator usage
    print("\n1️⃣ Traditional Decorator Usage:")
    greeting = generate_greeting("Alice", "support")
    print(f"Generated: {greeting}")
    
    # Test data pools
    print("\n2️⃣ Test Data Pools:")
    setup_test_pool()
    
    # Check if API is running for examples 3 & 4
    try:
        health = requests.get("http://localhost:8000/health")
        if health.status_code == 200:
            print("\n✅ API is running")
            
            # AI optimization
            print("\n3️⃣ AI-Powered Optimization:")
            optimize_greeting_prompt()
            
            # Combined usage
            print("\n4️⃣ Combined Decorator + Optimization:")
            result = asyncio.run(create_marketing_copy("AutoPromptix", "developers"))
            print(f"Result: {result}")
        else:
            print("\n⚠️  API not healthy")
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️  API not running. Start it with: python run.py --mode api")
        print("   Examples 3 & 4 require the API to be running.")
    
    print("\n" + "="*50)
    print("✅ Examples complete!")

if __name__ == "__main__":
    main()
