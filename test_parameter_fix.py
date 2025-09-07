#!/usr/bin/env python3
"""
Test that the parameter mapping fix is applied correctly
"""

import sys

def test_indexing_parameters():
    """Test that indexing uses correct parameters"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check that repository_path is used for create_research_repository
        if 'if index_tool_name == "create_research_repository":' in source:
            print("✅ Indexing tool conditional check exists")
        else:
            print("❌ Indexing tool conditional check missing")
            return False
        
        if '"repository_path": repository' in source:
            print("✅ repository_path parameter mapped correctly")
        else:
            print("❌ repository_path parameter not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking indexing parameters: {e}")
        return False

def test_search_parameters():
    """Test that search uses correct parameters"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check that index_path and limit are used for search_research_repository
        if 'if search_tool_name == "search_research_repository":' in source:
            print("✅ Search tool conditional check exists")
        else:
            print("❌ Search tool conditional check missing")
            return False
        
        if '"index_path": repository' in source:
            print("✅ index_path parameter mapped correctly")
        else:
            print("❌ index_path parameter not found")
            return False
        
        if '"limit": max_results' in source:
            print("✅ limit parameter mapped correctly")
        else:
            print("❌ limit parameter not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking search parameters: {e}")
        return False

def test_file_access_parameters():
    """Test that file access uses correct parameters"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check that filepath is used for access_file
        if 'if file_tool_name == "access_file":' in source:
            print("✅ File access tool conditional check exists")
        else:
            print("❌ File access tool conditional check missing")
            return False
        
        if 'f"{repo_name}/repository/{file_path}"' in source:
            print("✅ filepath parameter formatted correctly")
        else:
            print("❌ filepath parameter formatting not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking file access parameters: {e}")
        return False

def test_repository_structure_parameters():
    """Test that repository structure uses correct parameters"""
    try:
        with open('mcp_robust_client.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Check that filepath is used for access_file in structure
        if 'if structure_tool_name == "access_file":' in source:
            print("✅ Structure tool conditional check exists")
        else:
            print("❌ Structure tool conditional check missing")
            return False
        
        if 'f"{repo_name}/repository"' in source:
            print("✅ Structure filepath parameter formatted correctly")
        else:
            print("❌ Structure filepath parameter formatting not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking structure parameters: {e}")
        return False

def show_expected_fix():
    """Show what should happen now"""
    print("\n🎯 Expected Behavior After Parameter Fix")
    print("=" * 50)
    
    print("\n📚 **Repository Indexing**:")
    print("   Tool: create_research_repository")
    print("   Parameter: repository_path = 'https://github.com/satishk01/data-formulator.git'")
    print("   Result: ✅ Repository indexed successfully")
    
    print("\n🔍 **Repository Search**:")
    print("   Tool: search_research_repository")
    print("   Parameters: index_path='data-formulator', query='Python functions', limit=10")
    print("   Result: ✅ Search results returned")
    
    print("\n📄 **File Access**:")
    print("   Tool: access_file")
    print("   Parameter: filepath='data-formulator/repository/README.md'")
    print("   Result: ✅ File content returned")
    
    print("\n📁 **Repository Structure**:")
    print("   Tool: access_file")
    print("   Parameter: filepath='data-formulator/repository'")
    print("   Result: ✅ Directory listing returned")

def main():
    """Main test function"""
    print("🔧 Parameter Mapping Fix Verification")
    print("=" * 60)
    
    success = True
    
    print("\n🧪 Testing Parameter Mappings...")
    
    if not test_indexing_parameters():
        success = False
    
    if not test_search_parameters():
        success = False
    
    if not test_file_access_parameters():
        success = False
    
    if not test_repository_structure_parameters():
        success = False
    
    show_expected_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Parameter mapping fix verification passed!")
        print("\nThe MCP tools should now work with correct parameters:")
        print("• create_research_repository with repository_path")
        print("• search_research_repository with index_path and limit")
        print("• access_file with properly formatted filepath")
    else:
        print("❌ Some parameter mapping checks failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)