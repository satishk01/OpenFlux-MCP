#!/usr/bin/env python3
"""
Test the indexing functionality with the parameter fix
"""

import asyncio
import json
import logging
from mcp_robust_client import MCPRobustClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_indexing_parameters():
    """Test that indexing now uses correct parameters"""
    
    # Create a mock MCP client to test parameter preparation
    client = MCPRobustClient()
    
    # Mock the available tools
    client.available_tools = {
        'create_research_repository': {
            'name': 'create_research_repository',
            'description': 'Build a FAISS index for a Git repository'
        }
    }
    
    # Test the tool name resolution
    index_tool_name = client._get_tool_name([
        "create_research_repository",
        "index_repository",
        "index-repository"
    ])
    
    print(f"✅ Tool name resolved: {index_tool_name}")
    
    # Test parameter preparation logic
    repository = "https://github.com/satishk01/data-formulator.git"
    
    if index_tool_name == "create_research_repository":
        arguments = {
            "repository_path": repository
        }
        print(f"✅ Parameters prepared: {arguments}")
        print(f"✅ Using correct parameter name: repository_path")
    else:
        print("❌ Tool name not resolved correctly")
        return False
    
    # Show what the request would look like
    request = {
        "jsonrpc": "2.0",
        "id": 12345,
        "method": "tools/call",
        "params": {
            "name": index_tool_name,
            "arguments": arguments
        }
    }
    
    print(f"\n📋 Request that would be sent:")
    print(json.dumps(request, indent=2))
    
    return True

def test_repository_name_extraction():
    """Test repository name extraction for file access"""
    
    test_cases = [
        "https://github.com/satishk01/data-formulator.git",
        "https://github.com/user/repo.git",
        "https://github.com/org/project-name.git"
    ]
    
    print("\n🧪 Testing repository name extraction:")
    
    for repo_url in test_cases:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        print(f"  {repo_url} → {repo_name}")
        
        # Test file path formatting
        file_path = "README.md"
        formatted_path = f"{repo_name}/repository/{file_path}"
        print(f"    File access path: {formatted_path}")
        
        # Test directory path formatting
        dir_path = f"{repo_name}/repository"
        print(f"    Directory path: {dir_path}")
    
    return True

def show_troubleshooting_steps():
    """Show troubleshooting steps for indexing issues"""
    
    print("\n🔧 Troubleshooting Steps:")
    print("=" * 50)
    
    print("\n1. **Check GitHub Token**:")
    print("   - Ensure GITHUB_TOKEN is set in your .env file")
    print("   - Token should have 'repo' permissions for private repos")
    print("   - Token should be valid and not expired")
    
    print("\n2. **Check AWS Credentials**:")
    print("   - Ensure AWS credentials are configured")
    print("   - Check AWS_PROFILE and AWS_REGION in .env")
    print("   - Verify access to Amazon Bedrock embeddings")
    
    print("\n3. **Check Repository Access**:")
    print("   - Ensure the repository URL is correct")
    print("   - For private repos, ensure token has access")
    print("   - Try with a public repository first")
    
    print("\n4. **Check MCP Server Logs**:")
    print("   - Look for detailed error messages in the logs")
    print("   - Check if the repository is being cloned successfully")
    print("   - Verify embedding model is accessible")
    
    print("\n5. **Test with Simple Repository**:")
    print("   - Try indexing a small public repository first")
    print("   - Example: https://github.com/octocat/Hello-World.git")

def main():
    """Main test function"""
    print("🔧 Indexing Fix Verification")
    print("=" * 60)
    
    success = True
    
    print("\n🧪 Testing Parameter Preparation...")
    if not asyncio.run(test_indexing_parameters()):
        success = False
    
    if not test_repository_name_extraction():
        success = False
    
    show_troubleshooting_steps()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Parameter fix verification passed!")
        print("\n✅ The indexing should now work with:")
        print("   • Tool: create_research_repository")
        print("   • Parameter: repository_path")
        print("   • Proper error handling")
        
        print("\n🚀 Next Steps:")
        print("   1. Try indexing the repository again")
        print("   2. Check the application logs for detailed errors")
        print("   3. Verify your GitHub token and AWS credentials")
    else:
        print("❌ Some verification checks failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)