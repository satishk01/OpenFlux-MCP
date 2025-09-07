#!/usr/bin/env python3
"""
Test that the syntax fix worked and the app structure is correct
"""

import ast
import sys

def test_app_syntax():
    """Test that app.py has correct syntax"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        print("✅ app.py syntax is correct")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in app.py: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_mcp_client_syntax():
    """Test that mcp_robust_client.py has correct syntax"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the AST to check syntax
        ast.parse(source)
        print("✅ mcp_robust_client.py syntax is correct")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in mcp_robust_client.py: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error reading mcp_robust_client.py: {e}")
        return False

def check_method_structure():
    """Check that all methods are properly structured"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        # Find the OpenFluxApp class
        app_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'OpenFluxApp':
                app_class = node
                break
        
        if not app_class:
            print("❌ OpenFluxApp class not found")
            return False
        
        # Check for key methods
        methods = [node.name for node in app_class.body if isinstance(node, ast.FunctionDef)]
        
        expected_methods = [
            'handle_general_query',
            'handle_query_with_fallback', 
            'handle_file_request',
            'handle_repository_structure_request',
            'handle_code_search_request'
        ]
        
        missing_methods = [method for method in expected_methods if method not in methods]
        
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        
        print(f"✅ All expected methods found: {len(expected_methods)} methods")
        print(f"   Total methods in class: {len(methods)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking method structure: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Syntax Fix Verification")
    print("=" * 40)
    
    success = True
    
    # Test syntax
    if not test_app_syntax():
        success = False
    
    if not test_mcp_client_syntax():
        success = False
    
    # Test structure
    if not check_method_structure():
        success = False
    
    print("\\n" + "=" * 40)
    if success:
        print("🎉 All syntax and structure checks passed!")
        print("\\n📋 Verified:")
        print("• app.py syntax is correct")
        print("• mcp_robust_client.py syntax is correct") 
        print("• All expected methods are present")
        print("• Class structure is intact")
    else:
        print("❌ Some checks failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)