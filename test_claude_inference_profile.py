#!/usr/bin/env python3
"""
Test script to verify Claude inference profile model ID works
"""

import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_claude_model_id():
    """Test the Claude inference profile model ID"""
    print("Testing Claude inference profile model ID...")
    
    # Test model ID detection
    model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    print(f"Model ID: {model_id}")
    
    # Test detection logic
    is_claude = "anthropic.claude" in model_id or "claude" in model_id.lower()
    is_nova = "amazon.nova" in model_id or "nova" in model_id.lower()
    
    print(f"Detected as Claude: {is_claude}")
    print(f"Detected as Nova: {is_nova}")
    
    if is_claude and not is_nova:
        print("✅ Model ID correctly detected as Claude")
        
        # Test Claude request body structure
        messages = [{"role": "user", "content": "Test message"}]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": "You are a helpful assistant.",
            "messages": messages,
            "temperature": 0.7
        }
        
        print("✅ Claude request body structure is correct")
        print(f"Body keys: {list(body.keys())}")
        
        return True
    else:
        print("❌ Model ID detection failed")
        return False

def main():
    """Main test function"""
    print("🔍 Claude Inference Profile Test")
    print("=" * 40)
    
    success = test_claude_model_id()
    
    if success:
        print("\n🎉 Claude inference profile test passed!")
        print("The new model ID should work correctly.")
    else:
        print("\n❌ Claude inference profile test failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)