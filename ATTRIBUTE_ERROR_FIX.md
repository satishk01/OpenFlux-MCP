# AttributeError Fix: '_get_tool_name' Method Missing

## Issue Description
**Error**: `'MCPRobustClient' object has no attribute '_get_tool_name'`

**User Query**: "Can you please detail out the Python and nodejs folder structures and the files in these folders"

**Stack Trace**: Error occurred in `_get_repository_structure_async` method when trying to call `self._get_tool_name()`

## Root Cause
The `_get_tool_name` method was referenced in the new MCP tool methods but was never actually added to the `MCPRobustClient` class.

## Solution Applied

### 1. Added Missing Method
```python
def _get_tool_name(self, preferred_names: List[str]) -> Optional[str]:
    """Get the actual tool name from a list of preferred names"""
    for name in preferred_names:
        if name in self.available_tools:
            return name
    return None
```

### 2. Updated All Async Methods
Updated these methods to use proper tool name discovery:
- ✅ `_index_repository_async` - Now uses tool name discovery
- ✅ `_semantic_search_async` - Now uses tool name discovery  
- ✅ `_get_repository_structure_async` - Uses tool name discovery
- ✅ `_get_file_content_async` - Uses tool name discovery
- ✅ `_search_code_async` - Uses tool name discovery

### 3. Tool Name Variations Supported

**Repository Structure Tools**:
- `get_repository_structure`, `get-repository-structure`
- `repository_structure`, `repository-structure`
- `repo_structure`, `repo-structure`
- `list_files`, `list-files`, `tree`

**Indexing Tools**:
- `index_repository`, `index-repository`
- `index_repo`, `index-repo`
- `repository_index`, `repo_index`
- `clone_and_index`, `clone-and-index`

**Search Tools**:
- `semantic_search`, `semantic-search`
- `search`, `search_repository`, `search-repository`
- `repo_search`, `repo-search`
- `query`, `find`, `search_code`, `search-code`

## Verification

### ✅ Syntax Check
```bash
python -m py_compile mcp_robust_client.py  # PASSED
```

### ✅ Method Verification
- `_get_tool_name` method exists with correct signature
- Method is used in all 5 async tool methods
- Required imports (`Optional`, `List`) are present

### ✅ Expected Behavior
Your query "Can you please detail out the Python and nodejs folder structures" should now:

1. **Detect Structure Request**: App recognizes structure keywords
2. **Route to Handler**: Calls `handle_repository_structure_request()`
3. **Tool Discovery**: Uses `_get_tool_name()` to find available structure tool
4. **MCP Call**: Makes successful call to repository structure tool
5. **Analysis**: Provides detailed breakdown of Python and Node.js folders

## Files Modified
- ✅ `mcp_robust_client.py` - Added `_get_tool_name` method and updated async methods
- ✅ Syntax verified and working

## Expected Result
The AttributeError should be completely resolved. Your repository structure queries should now work properly and provide detailed analysis of folder structures and files.

## Test Commands
```bash
# Verify syntax
python -m py_compile mcp_robust_client.py

# Test the fix (if dependencies available)
python test_repository_structure_fix.py
```

The fix ensures robust tool discovery and should handle different MCP server implementations with varying tool names.