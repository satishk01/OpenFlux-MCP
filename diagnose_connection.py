#!/usr/bin/env python3
"""
Diagnostic tool for MCP connection issues
"""

import os
import sys
import time
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Check all prerequisites"""
    print("🔍 Checking Prerequisites...")
    issues = []
    
    # Check uvx
    try:
        result = subprocess.run(['uvx', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ uvx: {result.stdout.strip()}")
        else:
            issues.append("uvx command failed")
    except FileNotFoundError:
        issues.append("uvx not found - install with: pip install uv")
    except Exception as e:
        issues.append(f"uvx check failed: {e}")
    
    # Check GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        issues.append("GITHUB_TOKEN not set")
    elif github_token == 'your-github-token':
        issues.append("GITHUB_TOKEN is placeholder value")
    else:
        print(f"✅ GitHub token: {github_token[:8]}...")
    
    # Check AWS region
    aws_region = os.getenv('AWS_REGION', 'us-west-2')
    print(f"✅ AWS Region: {aws_region}")
    
    return issues

def test_mcp_server_startup():
    """Test if MCP server can start"""
    print("\n🚀 Testing MCP Server Startup...")
    
    try:
        env = os.environ.copy()
        env.update({
            "AWS_REGION": os.getenv("AWS_REGION", "us-west-2"),
            "FASTMCP_LOG_LEVEL": "INFO",
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
        })
        
        print("Starting MCP server process...")
        process = subprocess.Popen(
            ['uvx', 'awslabs.git-repo-research-mcp-server@latest'],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for startup
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ MCP server started successfully")
            
            # Try to send initialize request
            init_request = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"roots": {"listChanged": true}}, "clientInfo": {"name": "DiagnosticTest", "version": "1.0.0"}}}\n'
            
            try:
                process.stdin.write(init_request)
                process.stdin.flush()
                
                # Try to read response
                time.sleep(2)
                if process.poll() is None:
                    print("✅ MCP server accepting requests")
                else:
                    print("⚠️ MCP server died after initialize request")
                    
            except Exception as e:
                print(f"⚠️ Error communicating with MCP server: {e}")
            
            # Clean shutdown
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ MCP server terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Had to force kill MCP server")
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MCP server failed to start (exit code: {process.returncode})")
            if stderr:
                print(f"Error output: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

def test_robust_client():
    """Test the robust client"""
    print("\n🔧 Testing Robust Client...")
    
    try:
        from mcp_robust_client import MCPRobustClient
        
        client = MCPRobustClient()
        print("✅ Client created")
        
        # Test connection
        client.connect()
        print("✅ Connected")
        
        # Test health
        healthy = client.check_connection_health()
        print(f"✅ Health check: {healthy}")
        
        # Test cleanup
        client.cleanup()
        print("✅ Cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Robust client test failed: {e}")
        logger.error(f"Client test error: {e}", exc_info=True)
        return False

def main():
    """Main diagnostic function"""
    print("🩺 MCP Connection Diagnostic Tool")
    print("=" * 50)
    
    # Check prerequisites
    issues = check_prerequisites()
    if issues:
        print(f"\n❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   • {issue}")
        print("\nPlease fix these issues before proceeding.")
        return False
    
    print("\n✅ All prerequisites met")
    
    # Test MCP server
    if not test_mcp_server_startup():
        print("\n❌ MCP server startup failed")
        return False
    
    # Test robust client
    if not test_robust_client():
        print("\n❌ Robust client test failed")
        return False
    
    print("\n🎉 All diagnostic tests passed!")
    print("Your MCP connection should work correctly.")
    
    # Provide usage tips
    print("\n💡 Usage Tips:")
    print("• The app will auto-connect when you start it")
    print("• Index repositories before searching them")
    print("• Use the 'Auto-Fix Connection' button if issues occur")
    print("• Check the connection status indicator in the sidebar")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)