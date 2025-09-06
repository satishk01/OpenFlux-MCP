#!/usr/bin/env python3
"""
Test script for Bedrock client
Run this to verify the Bedrock client works correctly
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_bedrock_client():
    """Test the Bedrock client"""
    try:
        from bedrock_client import BedrockClient
        from aws_utils import test_aws_credentials, test_bedrock_access, get_ec2_instance_metadata
        
        print("🧪 Testing Bedrock Client...")
        
        # Check EC2 environment
        print("\n🔍 Checking EC2 environment...")
        ec2_info = get_ec2_instance_metadata()
        if ec2_info["is_ec2"]:
            print(f"✅ Running on EC2: {ec2_info['instance_id']}")
            if ec2_info["iam_role"]:
                print(f"✅ IAM Role: {ec2_info['iam_role']}")
            else:
                print("⚠️ No IAM role found")
        else:
            print("ℹ️ Not running on EC2")
        
        # Test AWS credentials
        print("\n🔍 Testing AWS credentials...")
        region = os.getenv('AWS_REGION', 'us-east-1')
        cred_test = test_aws_credentials(region)
        
        if cred_test["success"]:
            print(f"✅ AWS credentials working - Method: {cred_test['method']}")
            print(f"   Account: {cred_test['account']}")
        else:
            print(f"❌ AWS credentials failed: {cred_test['error']}")
            return False
        
        # Test Bedrock access
        print("\n🔍 Testing Bedrock access...")
        bedrock_test = test_bedrock_access(region)
        
        if bedrock_test["success"]:
            print(f"✅ Bedrock access working - {bedrock_test['models_available']} models available")
            if bedrock_test["claude_available"]:
                print("✅ Claude models available")
            if bedrock_test["nova_available"]:
                print("✅ Nova models available")
        else:
            print(f"❌ Bedrock access failed: {bedrock_test['error']}")
            return False
        
        # Test Bedrock client creation
        print("\n🔍 Testing Bedrock client creation...")
        client = BedrockClient(region=region)
        print(f"✅ Bedrock client created successfully")
        
        # Test a simple query
        print("\n🔍 Testing model invocation...")
        try:
            response = client.generate_response("Hello, can you respond with just 'Working!' to test the connection?")
            print(f"✅ Model response: {response[:100]}...")
        except Exception as e:
            print(f"❌ Model invocation failed: {e}")
            return False
        
        print("\n🎉 All Bedrock tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

def main():
    """Main test function"""
    print("🔍 Bedrock Client Test Suite")
    print("=" * 50)
    
    success = test_bedrock_client()
    
    if success:
        print("\n✅ Bedrock client is working correctly!")
        print("You can now use it in the Streamlit app.")
    else:
        print("\n❌ Bedrock client test failed.")
        print("Please check the error messages above.")
        print("\nCommon fixes:")
        print("- Ensure EC2 instance has proper IAM role with Bedrock permissions")
        print("- Remove invalid AWS credentials from environment variables")
        print("- Check that Bedrock is available in your region")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)