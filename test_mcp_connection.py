#!/usr/bin/env python3
"""
Test script for MCP connection
Run this to diagnose MCP server connection issues
"""

import os
import subprocess
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Check if all prerequisites are available"""
    print("🔍 Checking Prerequisites...")
    
    # Check uvx command
    try:
        result = subprocess.run(['uvx', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ uvx is available: {result.stdout.strip()}")
        else:
            print(f"❌ uvx command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ uvx command not found. Please install uv first:")
        print("   Visit: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    except subprocess.TimeoutExpired:
        print("❌ uvx command timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking uvx: {e}")
        return False
    
    # Check GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN not set in environment")
        print("   Please set your GitHub token in .env file")
        return False
    elif github_token == 'your-github-token':
        print("❌ GITHUB_TOKEN is still the placeholder value")
        print("   Please replace with your actual GitHub token")
        return False
    else:
        print(f"✅ GitHub token is set: {github_token[:8]}...")
    
    # Check AWS environment
    aws_region = os.getenv('AWS_REGION', 'us-west-2')
    aws_profile = os.getenv('AWS_PROFILE', 'default')
    print(f"✅ AWS Region: {aws_region}")
    print(f"✅ AWS Profile: {aws_profile}")
    
    return True

def test_mcp_server_start():
    """Test if the MCP server can start"""
    print("\n🚀 Testing MCP Server Start...")
    
    try:
        # Prepare environment
        env = os.environ.copy()
        env.update({
            "AWS_PROFILE": os.getenv("AWS_PROFILE", "default"),
            "AWS_REGION": os.getenv("AWS_REGION", "us-west-2"),
            "FASTMCP_LOG_LEVEL": "INFO",  # More verbose for testing
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
        })
        
        print("Starting MCP server process...")
        print("Command: uvx awslabs.git-repo-research-mcp-server@latest")
        
        # Start the process
        process = subprocess.Popen(
            ['uvx', 'awslabs.git-repo-research-mcp-server@latest'],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        import time
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ MCP server process started successfully")
            
            # Try to send a simple initialize request
            try:
                init_request = '''{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"roots": {"listChanged": true}, "sampling": {}}, "clientInfo": {"name": "OpenFlux", "version": "1.0.0"}}}
'''
                process.stdin.write(init_request)
                process.stdin.flush()
                
                # Try to read response (with timeout)
                import select
                if hasattr(select, 'select'):
                    ready, _, _ = select.select([process.stdout], [], [], 5)
                    if ready:
                        response = process.stdout.readline()
                        print(f"✅ MCP server responded: {response.strip()}")
                    else:
                        print("⚠️ MCP server didn't respond within 5 seconds")
                else:
                    # Windows doesn't have select, just try to read
                    response = process.stdout.readline()
                    if response:
                        print(f"✅ MCP server responded: {response.strip()}")
                    else:
                        print("⚠️ No response from MCP server")
                        
            except Exception as e:
                print(f"⚠️ Error communicating with MCP server: {e}")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ MCP server terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Had to force kill MCP server")
                
            return True
            
        else:
            # Process exited, check error
            stdout, stderr = process.communicate()
            print(f"❌ MCP server process exited with code: {process.returncode}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def test_sync_client():
    """Test the synchronous MCP client"""
    print("\n🔄 Testing Synchronous MCP Client...")
    
    try:
        from mcp_sync_client import MCPSyncClient
        
        client = MCPSyncClient()
        print("✅ MCPSyncClient created")
        
        # Try to connect
        print("Attempting to connect...")
        client.connect()
        print("✅ MCP client connected successfully")
        
        # Try to disconnect
        client.disconnect()
        print("✅ MCP client disconnected successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        logger.error(f"MCP client error: {e}", exc_info=True)
        return False

def main():
    """Main test function"""
    print("🔍 MCP Connection Diagnostic Test")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please fix the issues above.")
        return False
    
    # Test MCP server start
    if not test_mcp_server_start():
        print("\n❌ MCP server start test failed.")
        return False
    
    # Test sync client
    if not test_sync_client():
        print("\n❌ Sync client test failed.")
        return False
    
    print("\n🎉 All MCP connection tests passed!")
    print("The MCP server should work correctly in the Streamlit app.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)