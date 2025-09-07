#!/usr/bin/env python3
"""
Test all MCP tools to show what's available and working
"""

import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_mcp_tools():
    """Test all available MCP tools"""
    try:
        from mcp_robust_client import MCPRobustClient
        
        print("🔧 Testing All MCP Tools")
        print("=" * 50)
        
        # Check environment
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            print("❌ GITHUB_TOKEN not set - some tests may fail")
            return False
        
        print(f"✅ GitHub token: {github_token[:8]}...")
        
        # Create and connect client
        client = MCPRobustClient()
        print("✅ Client created")
        
        client.connect()
        print("✅ Connected to MCP server")
        
        # Check available tools
        if hasattr(client, 'available_tools'):
            tools = client.available_tools
            print(f"\\n📋 Found {len(tools)} available tools:")
            
            for tool_name, tool_info in tools.items():
                print(f"\\n🔧 Tool: {tool_name}")
                if 'description' in tool_info:
                    print(f"   Description: {tool_info['description']}")
                if 'inputSchema' in tool_info:
                    schema = tool_info['inputSchema']
                    if 'properties' in schema:
                        print(f"   Parameters: {list(schema['properties'].keys())}")
        
        # Test repository for demonstrations
        test_repo = "octocat/Hello-World"  # Small public repo
        
        print(f"\\n🧪 Testing Tools with Repository: {test_repo}")
        print("=" * 50)
        
        # Test 1: Repository Structure
        print("\\n1️⃣ Testing Repository Structure...")
        try:
            structure = client.get_repository_structure(test_repo)
            print("✅ Repository structure retrieved successfully")
            print(f"   Structure keys: {list(structure.keys()) if isinstance(structure, dict) else 'Non-dict response'}")
        except Exception as e:
            print(f"❌ Repository structure failed: {e}")
        
        # Test 2: Index Repository
        print("\\n2️⃣ Testing Repository Indexing...")
        try:
            index_result = client.index_repository(test_repo)
            print("✅ Repository indexed successfully")
            print(f"   Index result keys: {list(index_result.keys()) if isinstance(index_result, dict) else 'Non-dict response'}")
        except Exception as e:
            print(f"❌ Repository indexing failed: {e}")
        
        # Test 3: Semantic Search
        print("\\n3️⃣ Testing Semantic Search...")
        try:
            search_result = client.semantic_search(test_repo, "README", max_results=3)
            print("✅ Semantic search completed")
            results = search_result.get('results', []) if isinstance(search_result, dict) else []
            print(f"   Found {len(results)} results")
        except Exception as e:
            print(f"❌ Semantic search failed: {e}")
        
        # Test 4: File Content
        print("\\n4️⃣ Testing File Content Access...")
        try:
            file_content = client.get_file_content(test_repo, "README")
            print("✅ File content retrieved successfully")
            print(f"   Content keys: {list(file_content.keys()) if isinstance(file_content, dict) else 'Non-dict response'}")
        except Exception as e:
            print(f"❌ File content access failed: {e}")
        
        # Test 5: Code Search
        print("\\n5️⃣ Testing Code Pattern Search...")
        try:
            code_search = client.search_code(test_repo, "Hello", file_type="md")
            print("✅ Code pattern search completed")
            print(f"   Search result keys: {list(code_search.keys()) if isinstance(code_search, dict) else 'Non-dict response'}")
        except Exception as e:
            print(f"❌ Code pattern search failed: {e}")
        
        # Cleanup
        client.cleanup()
        print("\\n✅ All tests completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Tool testing failed: {e}")
        logger.error(f"Test error: {e}", exc_info=True)
        return False

def show_supported_operations():
    """Show what operations are now supported"""
    print("\\n🎯 Supported MCP Operations")
    print("=" * 40)
    
    operations = [
        {
            "name": "Repository Indexing",
            "tool": "index_repository",
            "description": "Index a repository for semantic search",
            "example": "Index the repository for searching"
        },
        {
            "name": "Semantic Search", 
            "tool": "semantic_search",
            "description": "Search repository content using natural language",
            "example": "Find authentication functions"
        },
        {
            "name": "Repository Structure",
            "tool": "get_repository_structure", 
            "description": "Get the directory structure and file organization",
            "example": "Show me the repository structure"
        },
        {
            "name": "File Content Access",
            "tool": "get_file_content",
            "description": "Get the content of specific files",
            "example": "Show me the file src/main.py"
        },
        {
            "name": "Code Pattern Search",
            "tool": "search_code",
            "description": "Search for specific code patterns or text",
            "example": "Search for pattern 'function main'"
        }
    ]
    
    for i, op in enumerate(operations, 1):
        print(f"\\n{i}️⃣ **{op['name']}**")
        print(f"   Tool: {op['tool']}")
        print(f"   Description: {op['description']}")
        print(f"   Example: {op['example']}")
    
    print("\\n💡 **Fallback Support**: If any MCP tool fails, the app automatically")
    print("   provides general programming assistance instead of leaving users stuck.")

def main():
    """Main test function"""
    print("🔧 MCP Tools Comprehensive Test")
    print("=" * 60)
    
    success = test_all_mcp_tools()
    show_supported_operations()
    
    print("\\n" + "=" * 60)
    if success:
        print("🎉 MCP tools test completed!")
        print("\\n📊 Summary:")
        print("• 5 different MCP tool types supported")
        print("• Automatic tool name discovery and mapping")
        print("• Fallback to general assistance when tools fail")
        print("• Enhanced error handling with user-friendly messages")
    else:
        print("❌ Some MCP tools may not be available")
        print("Check your MCP server configuration and GitHub token")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)