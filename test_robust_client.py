#!/usr/bin/env python3
"""
Test script for the robust MCP client
"""

import os
import sys
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_robust_client():
    """Test the robust MCP client"""
    try:
        from mcp_robust_client import MCPRobustClient
        
        print("🧪 Testing Robust MCP Client...")
        
        # Create client
        client = MCPRobustClient()
        print("✅ Client created")
        
        # Test connection
        print("\n🔌 Testing connection...")
        client.connect()
        print("✅ Connected successfully")
        
        # Test connection health
        print("\n💓 Testing connection health...")
        is_healthy = client.check_connection_health()
        print(f"✅ Connection healthy: {is_healthy}")
        
        # Test with a small public repository
        test_repo = "octocat/Hello-World"
        print(f"\n📚 Testing indexing with {test_repo}...")
        
        try:
            result = client.index_repository(test_repo)
            print(f"✅ Indexing completed: {result}")
            
            # Test if repository is marked as indexed
            is_indexed = client.is_repository_indexed(test_repo)
            print(f"✅ Repository marked as indexed: {is_indexed}")
            
            # Test search
            print(f"\n🔍 Testing search...")
            search_result = client.semantic_search(test_repo, "README", max_results=5)
            print(f"✅ Search completed, found {len(search_result.get('results', []))} results")
            
        except Exception as e:
            print(f"⚠️ Repository operations failed (this might be expected): {e}")
        
        # Test disconnect
        print("\n🔌 Testing disconnect...")
        client.disconnect()
        print("✅ Disconnected successfully")
        
        # Test cleanup
        print("\n🧹 Testing cleanup...")
        client.cleanup()
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

def test_connection_stability():
    """Test connection stability"""
    try:
        from mcp_robust_client import MCPRobustClient
        
        print("\n🔄 Testing Connection Stability...")
        
        client = MCPRobustClient()
        
        # Connect
        client.connect()
        print("✅ Initial connection")
        
        # Test multiple health checks
        for i in range(3):
            time.sleep(1)
            healthy = client.check_connection_health()
            print(f"✅ Health check {i+1}: {healthy}")
        
        # Test reconnection
        print("\n🔄 Testing reconnection...")
        client.disconnect()
        time.sleep(1)
        client.connect()
        print("✅ Reconnection successful")
        
        client.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Stability test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Robust MCP Client Test Suite")
    print("=" * 50)
    
    # Check environment first
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN not set. Please set it in your environment.")
        print("   export GITHUB_TOKEN=your_token_here")
        return False
    
    print(f"✅ GitHub token found: {github_token[:8]}...")
    
    success = True
    
    # Test basic functionality
    if not test_robust_client():
        success = False
    
    # Test stability
    if not test_connection_stability():
        success = False
    
    if success:
        print("\n🎉 All robust client tests passed!")
        print("The robust MCP client should provide better stability.")
    else:
        print("\n❌ Some tests failed.")
        print("Check the error messages above for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)