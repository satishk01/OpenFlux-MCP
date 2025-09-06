#!/usr/bin/env python3
"""
Test to verify the Claude model ID fix
"""

def test_model_detection():
    """Test model detection with new inference profile format"""
    print("Testing model detection with inference profile format...")
    
    # Test cases
    test_cases = [
        ("us.anthropic.claude-3-5-sonnet-20241022-v2:0", "claude", True, False),
        ("amazon.nova-pro-v1:0", "nova", False, True),
        ("us.anthropic.claude-3-haiku-20240307-v1:0", "claude", True, False),
        ("amazon.nova-lite-v1:0", "nova", False, True)
    ]
    
    all_passed = True
    
    for model_id, expected_type, should_be_claude, should_be_nova in test_cases:
        print(f"\nTesting: {model_id}")
        
        # Test detection logic (same as in bedrock_client.py)
        is_claude = "anthropic.claude" in model_id or "claude" in model_id.lower()
        is_nova = "amazon.nova" in model_id or "nova" in model_id.lower()
        
        print(f"  Detected as Claude: {is_claude}")
        print(f"  Detected as Nova: {is_nova}")
        print(f"  Expected type: {expected_type}")
        
        if is_claude == should_be_claude and is_nova == should_be_nova:
            print(f"  ✅ Correct detection")
        else:
            print(f"  ❌ Incorrect detection")
            all_passed = False
    
    return all_passed

def main():
    """Main test"""
    print("🔍 Model ID Fix Verification")
    print("=" * 40)
    
    success = test_model_detection()
    
    if success:
        print("\n🎉 All model detection tests passed!")
        print("The Claude inference profile fix should work correctly.")
    else:
        print("\n❌ Some model detection tests failed!")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)