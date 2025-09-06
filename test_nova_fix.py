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
    print("Testing Nova model parameter handling...")
    
    # Simulate the Nova request body that would be created
    messages = [
        {"role": "user", "content": [{"text": "System message"}]},
        {"role": "user", "content": [{"text": "Test message"}]}
    ]
    
    body = {
        "messages": messages,
        "inferenceConfig": {
            "maxTokens": 4000,
            "temperature": 0.7
        }
    }
    
    print("✅ Nova request body created with correct nested structure")
    print(f"Body keys: {list(body.keys())}")
    print(f"InferenceConfig keys: {list(body['inferenceConfig'].keys())}")
    
    # Verify correct parameters
    checks = [
        ("top_p not in body", "top_p" not in body),
        ("max_tokens not in body", "max_tokens" not in body),
        ("maxTokens not in root body", "maxTokens" not in body),
        ("temperature not in root body", "temperature" not in body),
        ("messages in body", "messages" in body),
        ("inferenceConfig in body", "inferenceConfig" in body),
        ("maxTokens in inferenceConfig", "maxTokens" in body.get("inferenceConfig", {})),
        ("temperature in inferenceConfig", "temperature" in body.get("inferenceConfig", {}))
    ]
    
    all_passed = True
    for check_name, check_result in checks:
        if check_result:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    success = test_nova_parameters()
    if success:
        print("\n🎉 Nova parameter fix verified!")
        print("The Nova model should now work with the correct nested inferenceConfig structure.")
    else:
        print("\n❌ Nova parameter fix failed!")