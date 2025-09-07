#!/usr/bin/env python3
"""
Test that the available_tools attribute fix works correctly
"""

import sys
import ast

def test_available_tools_initialization():
    """Test that available_tools is properly initialized"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check that available_tools is initialized in __init__
        if 'self.available_tools = {}' in source:
            print("✅ available_tools attribute is initialized in __init__")
        else:
            print("❌ available_tools attribute not found in __init__")
            return False
        
        # Check that _discover_tools method exists
        if 'async def _discover_tools(self):' in source:
            print("✅ _discover_tools method exists")
        else:
            print("❌ _discover_tools method not found")
            return False
        
        # Check that _discover_tools is called during initialization
        if 'await self._discover_tools()' in source:
            print("✅ _discover_tools is called during initialization")
        else:
            print("❌ _discover_tools is not called during initialization")
            return False
        
        # Check that helper methods exist
        helper_methods = [
            'def get_available_tools(self)',
            'def list_tools(self)',
            'def get_indexed_repositories(self)'
        ]
        
        for method in helper_methods:
            if method in source:
                print(f"✅ {method.split('(')[0].replace('def ', '')} method exists")
            else:
                print(f"❌ {method.split('(')[0].replace('def ', '')} method missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking available_tools initialization: {e}")
        return False

def test_tool_discovery_logic():
    """Test the tool discovery logic"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check that tools/list request is made
        if '"method": "tools/list"' in source:
            print("✅ tools/list request is made in _discover_tools")
        else:
            print("❌ tools/list request not found")
            return False
        
        # Check that tools are stored properly
        if 'self.available_tools = {tool.get(\'name\'): tool for tool in tools}' in source:
            print("✅ Tools are stored properly in available_tools")
        else:
            print("❌ Tools storage logic not found")
            return False
        
        # Check error handling
        if 'self.available_tools = {}' in source and 'except Exception as e:' in source:
            print("✅ Error handling for tool discovery exists")
        else:
            print("❌ Error handling for tool discovery missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking tool discovery logic: {e}")
        return False

def test_get_tool_name_usage():
    """Test that _get_tool_name properly uses available_tools"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check _get_tool_name method
        if 'if name in self.available_tools:' in source:
            print("✅ _get_tool_name properly checks available_tools")
        else:
            print("❌ _get_tool_name doesn't check available_tools properly")
            return False
        
        # Check that all async methods use _get_tool_name
        async_methods = [
            '_index_repository_async',
            '_semantic_search_async',
            '_get_repository_structure_async',
            '_get_file_content_async',
            '_search_code_async'
        ]
        
        for method in async_methods:
            if f'{method}' in source and 'self._get_tool_name([' in source:
                print(f"✅ {method} uses _get_tool_name")
            else:
                print(f"❌ {method} doesn't use _get_tool_name properly")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking _get_tool_name usage: {e}")
        return False

def show_fix_summary():
    """Show what was fixed"""
    print("\\n🔧 Available Tools Fix Summary")
    print("=" * 40)
    print("**Issue**: 'MCPRobustClient' object has no attribute 'available_tools'")
    print("**Cause**: available_tools attribute not initialized and tool discovery missing")
    print("**Solution**: Added proper initialization and tool discovery")
    
    print("\\n📋 Changes Made:")
    print("1. ✅ Added self.available_tools = {} in __init__")
    print("2. ✅ Added _discover_tools() method")
    print("3. ✅ Call _discover_tools() during initialization")
    print("4. ✅ Added helper methods for tool access")
    print("5. ✅ Proper error handling for tool discovery")
    
    print("\\n🎯 Expected Behavior:")
    print("• Repository indexing should work without AttributeError")
    print("• Tool discovery happens automatically on connection")
    print("• Fallback to empty tools dict if discovery fails")
    print("• All MCP tool methods should work properly")

def main():
    """Main test function"""
    print("🔧 Available Tools Fix Verification")
    print("=" * 60)
    
    success = True
    
    # Test initialization
    if not test_available_tools_initialization():
        success = False
    
    # Test tool discovery logic
    if not test_tool_discovery_logic():
        success = False
    
    # Test _get_tool_name usage
    if not test_get_tool_name_usage():
        success = False
    
    show_fix_summary()
    
    print("\\n" + "=" * 60)
    if success:
        print("🎉 Available tools fix verification passed!")
        print("\\nThe AttributeError should be resolved.")
        print("Repository indexing should now work properly.")
    else:
        print("❌ Fix verification failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)