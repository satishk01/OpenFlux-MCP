#!/usr/bin/env python3
"""
Test script for MCPSyncClient
Run this to verify the synchronous MCP client works correctly
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

def test_sync_client():
    """Test the synchronous MCP client"""
    try:
        from mcp_sync_client import MCPSyncClient
        
        print("🧪 Testing MCPSyncClient...")
        
        # Check environment
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            print("❌ GITHUB_TOKEN not set")
            return False
        
        print(f"✅ GitHub token: {github_token[:8]}...")
        
        # Create client
        client = MCPSyncClient()
        print(f"✅ Created client: {type(client)}")
        
        # Test connection
        print("🔄 Connecting to MCP server...")
        client.connect()
        print("✅ Connected successfully!")
        
        # Test repository indexing
        test_repo = "microsoft/calculator"  # Small repo for testing
        print(f"🔄 Indexing repository: {test_repo}")
        result = client.index_repository(test_repo)
        print(f"✅ Repository indexed: {result}")
        
        # Test semantic search
        print("🔄 Testing semantic search...")
        search_result = client.semantic_search(test_repo, "calculator functions", max_results=3)
        print(f"✅ Search completed: {len(search_result.get('matches', []))} results")
        
        # Cleanup
        print("🔄 Disconnecting...")
        client.disconnect()
        print("✅ Disconnected successfully!")
        
        print("🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

def main():
    """Main test function"""
    print("🔍 MCPSyncClient Test Suite")
    print("=" * 50)
    
    success = test_sync_client()
    
    if success:
        print("\n✅ MCPSyncClient is working correctly!")
        print("You can now use it in the Streamlit app.")
    else:
        print("\n❌ MCPSyncClient test failed.")
        print("Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)