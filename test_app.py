#!/usr/bin/env python3
"""
Test script for OpenFlux application
Run this to verify the application works correctly
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import boto3
        print("✅ Boto3 imported successfully")
    except ImportError as e:
        print(f"❌ Boto3 import failed: {e}")
        return False
    
    try:
        from mcp_client import MCPClient
        print("✅ MCP Client imported successfully")
    except ImportError as e:
        print(f"❌ MCP Client import failed: {e}")
        return False
    
    try:
        from bedrock_client import BedrockClient
        print("✅ Bedrock Client imported successfully")
    except ImportError as e:
        print(f"❌ Bedrock Client import failed: {e}")
        return False
    
    try:
        from config import Config
        print("✅ Config imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration validation"""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import Config
        validation = Config.validate_config()
        
        print(f"Configuration valid: {validation['valid']}")
        if validation['issues']:
            print("Issues found:")
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        print(f"AWS Region: {validation['config']['aws_region']}")
        print(f"GitHub Token Set: {validation['config']['github_token_set']}")
        print(f"Default Model: {validation['config']['default_model']}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_bedrock_client():
    """Test Bedrock client initialization"""
    print("\n☁️ Testing Bedrock client...")
    
    try:
        from bedrock_client import BedrockClient
        
        # Test client initialization
        client = BedrockClient()
        print("✅ Bedrock client initialized successfully")
        
        # Test model validation
        claude_client = BedrockClient(model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        nova_client = BedrockClient(model_id="amazon.nova-pro-v1:0")
        print("✅ Model configurations validated")
        
        return True
    except Exception as e:
        print(f"❌ Bedrock client test failed: {e}")
        return False

async def test_mcp_client():
    """Test MCP client initialization"""
    print("\n🔄 Testing MCP client...")
    
    try:
        from mcp_client import MCPClient
        
        # Test client initialization
        client = MCPClient()
        print("✅ MCP client initialized successfully")
        
        # Test configuration
        if client.server_config:
            print("✅ MCP server configuration loaded")
        
        return True
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        return False

def test_utils():
    """Test utility functions"""
    print("\n🛠️ Testing utilities...")
    
    try:
        from utils import (
            format_timestamp, 
            safe_json_loads, 
            extract_repository_info,
            validate_github_repo
        )
        
        # Test timestamp formatting
        timestamp = format_timestamp()
        print(f"✅ Timestamp: {timestamp}")
        
        # Test JSON parsing
        test_json = '{"test": "value"}'
        parsed = safe_json_loads(test_json)
        assert parsed["test"] == "value"
        print("✅ JSON parsing works")
        
        # Test repository info extraction
        repo_info = extract_repository_info("microsoft/vscode")
        assert repo_info["owner"] == "microsoft"
        assert repo_info["repo"] == "vscode"
        print("✅ Repository info extraction works")
        
        # Test repository validation
        assert validate_github_repo("microsoft/vscode") == True
        assert validate_github_repo("invalid") == False
        print("✅ Repository validation works")
        
        return True
    except Exception as e:
        print(f"❌ Utilities test failed: {e}")
        return False

def check_environment():
    """Check environment setup"""
    print("\n🌍 Checking environment...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found (using .env.example as template)")
    
    # Check critical environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        print("✅ GITHUB_TOKEN is set")
    else:
        print("⚠️ GITHUB_TOKEN not set - MCP server may not work")
    
    aws_region = os.getenv('AWS_REGION', 'us-west-2')
    print(f"✅ AWS Region: {aws_region}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 OpenFlux Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("Bedrock Client Tests", test_bedrock_client),
        ("MCP Client Tests", lambda: asyncio.run(test_mcp_client())),
        ("Utility Tests", test_utils),
        ("Environment Check", check_environment)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenFlux is ready to run.")
        print("\nTo start the application:")
        print("  streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        print("\nCommon fixes:")
        print("  - Install missing dependencies: pip install -r requirements.txt")
        print("  - Set up environment variables in .env file")
        print("  - Configure AWS credentials: aws configure")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)