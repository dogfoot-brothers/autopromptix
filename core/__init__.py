"""
AutoPromptix - AI-Powered Automated Prompt Testing and Optimization

A comprehensive platform for testing and optimizing AI prompts automatically.
"""

from .decorators import (
    selftest,
    desiredoutput,
    self_test_system_prompt,
    self_test_temperature,
    self_test_k,
    client
)
from .decorators import (
    test,
    test_config,
    prompt_template,
    test_context,
    auto_test,
    autopromptix
)
from .decorators import get_test_registry, get_function_metadata
from .storage import StorageManager
from .prompt_improver import PromptImprover
from .test_runner import TestRunner
from .test_data_pool import TestDataPoolManager, TestDataPool, TestCase

# Import new AI-powered components
try:
    from .prompt_optimizer import PromptOptimizer, optimize_prompt_simple, optimize_prompt_streaming
    from .scorer import (
        cosine_similarity, rouge_l_score, keyword_coverage, 
        structure_score, composite_score, final_score_with_forbidden_check,
        evaluate_prompt_quality
    )
    from .llm_integration import (
        LLMProvider, OpenAIProvider, AnthropicProvider, MockProvider,
        get_provider, ask_llm, set_provider, reset_provider
    )
    AI_FEATURES_AVAILABLE = True
except ImportError as e:
    AI_FEATURES_AVAILABLE = False
    import warnings
    warnings.warn(f"AI features not available: {e}")

__version__ = "1.0.0"
__author__ = "AutoPromptix Team"

# Initialize storage and core components
storage = StorageManager()
prompt_improver = PromptImprover(storage)
test_runner = TestRunner(storage, prompt_improver)
test_data_manager = TestDataPoolManager()

__all__ = [
    # Legacy decorators
    'selftest',
    'desiredoutput', 
    'self_test_system_prompt',
    'self_test_temperature',
    'self_test_k',
    'client',
    # Enhanced decorators
    'test',
    'test_config',
    'prompt_template',
    'test_context',
    'auto_test',
    'autopromptix',
    # Core components
    'storage',
    'prompt_improver',
    'test_runner',
    'test_data_manager',
    # Functions
    'get_test_registry',
    'get_function_metadata',
    # Data models
    'TestDataPool',
    'TestCase',
    # AI features (if available)
    'AI_FEATURES_AVAILABLE'
]

# Add AI features to exports if available
if AI_FEATURES_AVAILABLE:
    __all__.extend([
        # Optimizer
        'PromptOptimizer',
        'optimize_prompt_simple',
        'optimize_prompt_streaming',
        # Scorer
        'cosine_similarity',
        'rouge_l_score',
        'keyword_coverage',
        'structure_score',
        'composite_score',
        'final_score_with_forbidden_check',
        'evaluate_prompt_quality',
        # LLM Integration
        'LLMProvider',
        'OpenAIProvider',
        'AnthropicProvider',
        'MockProvider',
        'get_provider',
        'ask_llm',
        'set_provider',
        'reset_provider'
    ]) 