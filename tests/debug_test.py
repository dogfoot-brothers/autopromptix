"""
Debug test for PromptImprover issue
"""
import tempfile
import shutil
import traceback

from autopromptix.storage import StorageManager
from autopromptix.prompt_improver import PromptImprover

def debug_prompt_improver():
    """Debug the PromptImprover functionality"""
    print("🔍 Debugging PromptImprover...")
    
    try:
        temp_dir = tempfile.mkdtemp()
        print(f"Created temp directory: {temp_dir}")
        
        storage = StorageManager(temp_dir)
        print("StorageManager created successfully")
        
        improver = PromptImprover(storage)
        print("PromptImprover created successfully")
        
        # Test prompt parsing
        prompt = "You are a helpful assistant. 1. Be polite. 2. Be accurate. Do not be harmful."
        print(f"Testing prompt: {prompt}")
        
        parsed = improver.parse_system_prompt(prompt)
        print(f"Parsed result: {parsed}")
        
        print(f"Word count: {parsed['word_count']}")
        print(f"Instructions: {parsed['instructions']}")
        print(f"Instructions length: {len(parsed['instructions'])}")
        
        # Test prompt analysis
        print("Testing prompt analysis...")
        analysis = improver.analyze_prompt(prompt)
        print(f"Analysis result: {analysis}")
        
        print(f"Clarity score: {analysis.clarity_score}")
        print(f"Specificity score: {analysis.specificity_score}")
        print(f"Completeness score: {analysis.completeness_score}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print("✅ PromptImprover debug completed successfully")
        
    except Exception as e:
        print(f"❌ Error in PromptImprover: {e}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_prompt_improver() 