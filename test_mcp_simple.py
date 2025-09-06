#!/usr/bin/env python3
"""
Simple MCP connection test without external dependencies
"""

import os
import subprocess
import sys

def check_uvx():
    """Check if uvx is available"""
    print("🔍 Checking uvx availability...")
    
    try:
        result = subprocess.run(['uvx', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ uvx is available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ uvx command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ uvx command not found")
        print("Please install uv first:")
        print("  pip install uv")
        print("  or visit: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    except Exception as e:
        print(f"❌ Error checking uvx: {e}")
        return False

def check_github_token():
    """Check GitHub token"""
    print("\n🔍 Checking GitHub token...")
    
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token:")
        print("  set GITHUB_TOKEN=your_token_here")
        return False
    elif github_token == 'your-github-token':
        print("❌ GITHUB_TOKEN is still the placeholder value")
        return False
    else:
        print(f"✅ GitHub token is set: {github_token[:8]}...")
        return True

def test_mcp_server():
    """Test MCP server startup"""
    print("\n🚀 Testing MCP server startup...")
    
    try:
        # Set up environment
        env = os.environ.copy()
        env.update({
            "AWS_REGION": os.getenv("AWS_REGION", "us-west-2"),
            "FASTMCP_LOG_LEVEL": "INFO",
            "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
        })
        
        print("Starting: uvx awslabs.git-repo-research-mcp-server@latest")
        
        # Start process
        process = subprocess.Popen(
            ['uvx', 'awslabs.git-repo-research-mcp-server@latest'],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for startup
        import time
        time.sleep(3)
        
        # Check if running
        if process.poll() is None:
            print("✅ MCP server started successfully")
            
            # Clean shutdown
            process.terminate()
            try:
                process.wait(timeout=3)
                print("✅ MCP server terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Had to force kill MCP server")
            
            return True
        else:
            # Process failed
            stdout, stderr = process.communicate()
            print(f"❌ MCP server failed to start (exit code: {process.returncode})")
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def main():
    """Main test"""
    print("🔍 Simple MCP Connection Test")
    print("=" * 40)
    
    all_good = True
    
    if not check_uvx():
        all_good = False
    
    if not check_github_token():
        all_good = False
    
    if all_good:
        if test_mcp_server():
            print("\n🎉 MCP server test passed!")
            print("The MCP connection should work in the app.")
        else:
            print("\n❌ MCP server test failed.")
            all_good = False
    else:
        print("\n❌ Prerequisites not met. Please fix the issues above.")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)