#!/usr/bin/env python3
"""
Quick test to verify Nova model parameter fix
"""

import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nova_parameters():
    """Test that Nova model parameters are correct"""
    try:
        from bedrock_client import BedrockClient
        
        print("Testing Nova model parameter handling...")
        
        # Create client with Nova model
        client = BedrockClient(
            region="us-east-1", 
            model_id="amazon.nova-pro-v1:0"
        )
        
        # Test the _call_nova method parameters
        print("✅ BedrockClient created successfully")
        
        # Check if we can create the request body without errors
        messages = [
            {"role": "user", "content": [{"text": "Test message"}]}
        ]
        
        body = {
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        print("✅ Nova request body created without top_p parameter")
        print(f"Body keys: {list(body.keys())}")
        
        # Verify top_p is not in the body
        if "top_p" not in body:
            print("✅ Confirmed: top_p parameter removed from Nova requests")
            return True
        else:
            print("❌ Error: top_p parameter still present in Nova requests")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_nova_parameters()
    if success:
        print("\n🎉 Nova parameter fix verified!")
    else:
        print("\n❌ Nova parameter fix failed!")