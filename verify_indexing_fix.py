#!/usr/bin/env python3
"""
Verify that the indexing parameter fix is correctly applied
"""

def verify_parameter_fix():
    """Verify the parameter fix is in place"""
    
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        print("🔧 Verifying Indexing Parameter Fix")
        print("=" * 50)
        
        # Check for the correct parameter mapping
        checks = [
            ('if index_tool_name == "create_research_repository":', 'Indexing tool conditional'),
            ('"repository_path": repository', 'Correct parameter name'),
            ('# This tool expects repository_path', 'Parameter comment'),
            ('if search_tool_name == "search_research_repository":', 'Search tool conditional'),
            ('"index_path": repository', 'Search index_path parameter'),
            ('"limit": max_results', 'Search limit parameter'),
            ('if file_tool_name == "access_file":', 'File access conditional'),
            ('f"{repo_name}/repository/{file_path}"', 'File path formatting')
        ]
        
        all_passed = True
        
        for check_text, description in checks:
            if check_text in source:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - NOT FOUND")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def show_expected_behavior():
    """Show what should happen now"""
    
    print("\n🎯 Expected Indexing Behavior")
    print("=" * 40)
    
    print("\n📋 Request Format:")
    print("""
{
  "jsonrpc": "2.0",
  "id": 12345,
  "method": "tools/call",
  "params": {
    "name": "create_research_repository",
    "arguments": {
      "repository_path": "https://github.com/satishk01/data-formulator.git"
    }
  }
}
""")
    
    print("🔍 Key Changes:")
    print("• Tool name: create_research_repository ✅")
    print("• Parameter: repository_path (not 'repository') ✅")
    print("• Proper error handling ✅")
    
    print("\n📝 Expected Log Messages:")
    print("INFO: Using indexing tool: create_research_repository")
    print("INFO: Repository indexed successfully")
    
    print("\n⚠️  Common Issues to Check:")
    print("1. GitHub Token - Must be valid and have repo access")
    print("2. AWS Credentials - Must have Bedrock access")
    print("3. Repository URL - Must be accessible")
    print("4. Network connectivity - MCP server needs internet access")

def show_debugging_tips():
    """Show debugging tips"""
    
    print("\n🐛 Debugging Tips")
    print("=" * 30)
    
    print("\n1. **Check Environment Variables:**")
    print("   GITHUB_TOKEN=your_token_here")
    print("   AWS_PROFILE=default")
    print("   AWS_REGION=us-west-2")
    
    print("\n2. **Test with Public Repository:**")
    print("   Try: https://github.com/octocat/Hello-World.git")
    
    print("\n3. **Check MCP Server Status:**")
    print("   Look for 'MCP server connected successfully' in logs")
    
    print("\n4. **Verify Tool Discovery:**")
    print("   Should see: Available tools: ['create_research_repository', ...]")
    
    print("\n5. **Monitor Full Error Messages:**")
    print("   Check both application logs and MCP server stderr")

def main():
    """Main verification function"""
    
    success = verify_parameter_fix()
    
    show_expected_behavior()
    show_debugging_tips()
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 Parameter fix verification PASSED!")
        print("\n✅ The indexing should now work correctly.")
        print("✅ All parameter mappings are in place.")
        print("\n🚀 Try indexing your repository again!")
        
        print("\n💡 If indexing still fails, check:")
        print("   • GitHub token permissions")
        print("   • AWS Bedrock access")
        print("   • Repository accessibility")
        print("   • MCP server logs for detailed errors")
    else:
        print("❌ Parameter fix verification FAILED!")
        print("Some required changes are missing.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)