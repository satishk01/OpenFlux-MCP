#!/usr/bin/env python3
"""
Test that the _get_tool_name method fix works correctly
"""

import sys
import ast

def test_get_tool_name_method_exists():
    """Test that _get_tool_name method exists in MCPRobustClient"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        # Find the MCPRobustClient class
        client_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'MCPRobustClient':
                client_class = node
                break
        
        if not client_class:
            print("❌ MCPRobustClient class not found")
            return False
        
        # Check for _get_tool_name method
        methods = [node.name for node in client_class.body if isinstance(node, ast.FunctionDef)]
        
        if '_get_tool_name' not in methods:
            print("❌ _get_tool_name method not found")
            print(f"Available methods: {methods}")
            return False
        
        print("✅ _get_tool_name method found in MCPRobustClient")
        
        # Check method signature
        for node in client_class.body:
            if isinstance(node, ast.FunctionDef) and node.name == '_get_tool_name':
                args = [arg.arg for arg in node.args.args]
                if 'self' in args and 'preferred_names' in args:
                    print("✅ _get_tool_name method has correct signature")
                    return True
                else:
                    print(f"❌ _get_tool_name method has incorrect signature: {args}")
                    return False
        
        return False
        
    except Exception as e:
        print(f"❌ Error checking _get_tool_name method: {e}")
        return False

def test_method_usage():
    """Test that _get_tool_name is used in the async methods"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check if _get_tool_name is called in the async methods
        methods_using_get_tool_name = []
        
        if 'self._get_tool_name([' in source:
            # Count occurrences
            occurrences = source.count('self._get_tool_name([')
            print(f"✅ _get_tool_name is used {occurrences} times in the code")
            
            # Check specific methods
            if '_index_repository_async' in source and 'index_tool_name = self._get_tool_name([' in source:
                methods_using_get_tool_name.append('_index_repository_async')
            
            if '_semantic_search_async' in source and 'search_tool_name = self._get_tool_name([' in source:
                methods_using_get_tool_name.append('_semantic_search_async')
            
            if '_get_repository_structure_async' in source and 'structure_tool_name = self._get_tool_name([' in source:
                methods_using_get_tool_name.append('_get_repository_structure_async')
            
            if '_get_file_content_async' in source and 'file_tool_name = self._get_tool_name([' in source:
                methods_using_get_tool_name.append('_get_file_content_async')
            
            if '_search_code_async' in source and 'code_search_tool_name = self._get_tool_name([' in source:
                methods_using_get_tool_name.append('_search_code_async')
            
            print(f"✅ Methods using _get_tool_name: {methods_using_get_tool_name}")
            return len(methods_using_get_tool_name) >= 3  # At least 3 methods should use it
        else:
            print("❌ _get_tool_name is not used in the code")
            return False
        
    except Exception as e:
        print(f"❌ Error checking method usage: {e}")
        return False

def test_imports():
    """Test that required imports are present"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        required_imports = ['Optional', 'List']
        missing_imports = []
        
        for imp in required_imports:
            if imp not in source:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"❌ Missing imports: {missing_imports}")
            return False
        
        print("✅ All required imports are present")
        return True
        
    except Exception as e:
        print(f"❌ Error checking imports: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 _get_tool_name Fix Verification")
    print("=" * 50)
    
    success = True
    
    # Test method exists
    if not test_get_tool_name_method_exists():
        success = False
    
    # Test method usage
    if not test_method_usage():
        success = False
    
    # Test imports
    if not test_imports():
        success = False
    
    print("\\n" + "=" * 50)
    if success:
        print("🎉 _get_tool_name fix verification passed!")
        print("\\n📋 Verified:")
        print("• _get_tool_name method exists with correct signature")
        print("• Method is used in multiple async tool methods")
        print("• Required imports are present")
        print("• Should fix the AttributeError")
    else:
        print("❌ Some verification checks failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)