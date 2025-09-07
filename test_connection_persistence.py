#!/usr/bin/env python3
"""
Test connection persistence and stability
"""

import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection_persistence():
    """Test that connections persist through multiple operations"""
    try:
        from mcp_robust_client import MCPRobustClient
        
        print("🔄 Testing Connection Persistence...")
        
        # Check environment first
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            print("❌ GITHUB_TOKEN not set")
            return False
        
        client = MCPRobustClient()
        
        # Initial connection
        print("\n1️⃣ Initial connection...")
        client.connect()
        print("✅ Connected")
        
        # Test multiple health checks
        print("\n2️⃣ Testing health checks...")
        for i in range(5):
            healthy = client.check_connection_health()
            print(f"   Health check {i+1}: {'✅' if healthy else '❌'}")
            if not healthy:
                print("❌ Connection became unhealthy")
                return False
            time.sleep(1)
        
        # Test operations don't break connection
        print("\n3️⃣ Testing operations...")
        try:
            # Try a simple operation (this might fail but shouldn't break connection)
            result = client.index_repository("octocat/Hello-World")
            print("✅ Index operation completed")
        except Exception as e:
            print(f"⚠️ Index operation failed (expected): {e}")
        
        # Check connection is still healthy after operation
        healthy = client.check_connection_health()
        print(f"   Connection after operation: {'✅' if healthy else '❌'}")
        
        if not healthy:
            print("❌ Connection broke after operation")
            return False
        
        # Test search operation
        try:
            result = client.semantic_search("octocat/Hello-World", "README", max_results=3)
            print("✅ Search operation completed")
        except Exception as e:
            print(f"⚠️ Search operation failed (might be expected): {e}")
        
        # Final health check
        healthy = client.check_connection_health()
        print(f"   Final connection status: {'✅' if healthy else '❌'}")
        
        # Cleanup
        print("\n4️⃣ Testing cleanup...")
        client.cleanup()
        print("✅ Cleanup completed")
        
        return healthy
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

def test_reconnection():
    """Test automatic reconnection"""
    try:
        from mcp_robust_client import MCPRobustClient
        
        print("\n🔄 Testing Reconnection...")
        
        client = MCPRobustClient()
        
        # Connect
        client.connect()
        print("✅ Initial connection")
        
        # Simulate connection loss by disconnecting
        client.disconnect()
        print("🔌 Disconnected")
        
        # Try to reconnect
        client.connect()
        print("✅ Reconnected")
        
        # Verify it's healthy
        healthy = client.check_connection_health()
        print(f"   Reconnection health: {'✅' if healthy else '❌'}")
        
        client.cleanup()
        return healthy
        
    except Exception as e:
        print(f"❌ Reconnection test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Connection Persistence Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test persistence
    if not test_connection_persistence():
        success = False
    
    # Test reconnection
    if not test_reconnection():
        success = False
    
    if success:
        print("\n🎉 All connection persistence tests passed!")
        print("The MCP connection should remain stable during operations.")
    else:
        print("\n❌ Some connection tests failed.")
        print("Check the error messages above for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)