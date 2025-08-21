"""
AutoPromptix LLM Integration

Handles integration with various LLM providers (OpenAI, Anthropic, etc.)
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import LLM libraries
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available")

class LLMProvider:
    """Base class for LLM providers"""
    
    async def ask(self, system_prompt: str, user_input: str, **kwargs) -> str:
        """Send a request to the LLM and get response"""
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def ask(self, system_prompt: str, user_input: str, **kwargs) -> str:
        """Send request to OpenAI"""
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1000),
                top_p=kwargs.get('top_p', 1),
                frequency_penalty=kwargs.get('frequency_penalty', 0),
                presence_penalty=kwargs.get('presence_penalty', 0)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-opus-20240229"):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
    
    async def ask(self, system_prompt: str, user_input: str, **kwargs) -> str:
        """Send request to Anthropic"""
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

class MockProvider(LLMProvider):
    """Mock provider for testing without API keys"""
    
    async def ask(self, system_prompt: str, user_input: str, **kwargs) -> str:
        """Generate mock response"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Generate different responses based on input
        responses = [
            f"Based on your request '{user_input}', here's a comprehensive response that addresses your needs.",
            f"I understand you're asking about '{user_input}'. Let me provide you with detailed information.",
            f"Thank you for your question about '{user_input}'. Here's my analysis and recommendations.",
            f"Regarding '{user_input}', I've prepared a thorough response covering all key aspects.",
            f"Your request about '{user_input}' is interesting. Here's my detailed perspective on this topic."
        ]
        
        import random
        base_response = random.choice(responses)
        
        # Add some structured content
        structured_content = """

## Key Points

1. **First Point**: This is an important consideration that directly addresses your request.
2. **Second Point**: Additional context that provides deeper understanding.
3. **Third Point**: Practical applications and real-world examples.

## Detailed Analysis

The topic you've raised involves several interconnected factors. Let me break down each component:

- **Component A**: This forms the foundation of our approach
- **Component B**: Builds upon the first element with additional complexity
- **Component C**: Ties everything together for a comprehensive solution

## Recommendations

Based on the analysis above, I recommend:

1. Start with a pilot implementation
2. Gather feedback and iterate
3. Scale gradually based on results

## Conclusion

This approach ensures you achieve your objectives while maintaining flexibility for future adjustments."""
        
        return base_response + structured_content

# Global provider instance
_provider: Optional[LLMProvider] = None

def get_provider(provider_type: str = None) -> LLMProvider:
    """Get or create LLM provider instance"""
    global _provider
    
    if _provider is None:
        if provider_type is None:
            # Auto-detect based on available API keys
            if os.getenv("OPENAI_API_KEY") and OPENAI_AVAILABLE:
                provider_type = "openai"
            elif os.getenv("ANTHROPIC_API_KEY") and ANTHROPIC_AVAILABLE:
                provider_type = "anthropic"
            else:
                provider_type = "mock"
        
        if provider_type == "openai":
            _provider = OpenAIProvider()
        elif provider_type == "anthropic":
            _provider = AnthropicProvider()
        else:
            _provider = MockProvider()
            logger.info("Using mock LLM provider (no API keys found)")
    
    return _provider

async def ask_llm(
    prompt: str, 
    user_input: str, 
    provider_type: str = None,
    **kwargs
) -> str:
    """
    Send a request to the LLM and get response
    
    Args:
        prompt: System prompt or full prompt
        user_input: User input/question
        provider_type: Optional provider type override
        **kwargs: Additional parameters for the LLM
    
    Returns:
        LLM response as string
    """
    provider = get_provider(provider_type)
    
    # If prompt contains both system and user parts, use as system prompt
    # Otherwise, combine prompt and user_input
    if user_input:
        system_prompt = prompt
    else:
        system_prompt = "You are a helpful assistant."
        user_input = prompt
    
    return await provider.ask(system_prompt, user_input, **kwargs)

def set_provider(provider: LLMProvider):
    """Set a custom LLM provider"""
    global _provider
    _provider = provider

def reset_provider():
    """Reset the global provider instance"""
    global _provider
    _provider = None
