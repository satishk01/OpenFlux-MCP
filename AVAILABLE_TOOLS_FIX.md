# Available Tools AttributeError Fix

## Issue Description
**Error**: `'MCPRobustClient' object has no attribute 'available_tools'`

**Context**: When trying to index a repository, the error occurred in the `_get_tool_name` method when it tried to access `self.available_tools`.

**Stack Trace**: Error in `_index_repository_async` → `_get_tool_name` → `self.available_tools`

## Root Cause Analysis
1. **Missing Attribute**: `available_tools` was not initialized in the `__init__` method
2. **Missing Tool Discovery**: No mechanism to discover what tools are available from the MCP server
3. **Incomplete Implementation**: The `_get_tool_name` method expected `available_tools` to exist but it was never created

## Solution Applied

### 1. Initialize available_tools Attribute
```python
def __init__(self):
    # ... existing initialization ...
    self.available_tools = {}  # Store available tools
```

### 2. Added Tool Discovery Method
```python
async def _discover_tools(self):
    """Discover what tools are available from the MCP server"""
    try:
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await self._send_request(tools_request)
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            logger.info(f"Available tools: {[tool.get('name', 'unknown') for tool in tools]}")
            
            # Store tool names for reference
            self.available_tools = {tool.get('name'): tool for tool in tools}
            
            # Log tool details for debugging
            for tool in tools:
                logger.info(f"Tool: {tool.get('name')} - {tool.get('description', 'No description')}")
        else:
            logger.warning(f"Unexpected tools/list response: {response}")
            self.available_tools = {}
            
    except Exception as e:
        logger.error(f"Failed to discover tools: {e}")
        self.available_tools = {}
```

### 3. Call Tool Discovery During Initialization
```python
async def _initialize_protocol(self):
    # ... existing initialization ...
    logger.info("MCP protocol initialized")
    
    # Discover available tools
    await self._discover_tools()
```

### 4. Added Helper Methods
```python
def get_available_tools(self) -> Dict[str, Any]:
    """Get list of available tools"""
    return self.available_tools.copy()
    
def list_tools(self) -> List[str]:
    """Get list of available tool names"""
    return list(self.available_tools.keys())
    
def get_indexed_repositories(self) -> List[str]:
    """Get list of indexed repositories"""
    return list(self.indexed_repositories)
```

## How It Works Now

### 1. Connection Flow
1. **Connect**: `connect()` method starts MCP server process
2. **Initialize**: `_initialize_protocol()` sends initialize request
3. **Discover Tools**: `_discover_tools()` queries available tools
4. **Store Tools**: Tools are stored in `self.available_tools`

### 2. Tool Usage Flow
1. **Tool Request**: User tries to index repository
2. **Tool Discovery**: `_get_tool_name()` checks `self.available_tools`
3. **Tool Selection**: Finds best matching tool name
4. **Tool Call**: Uses discovered tool name for MCP request

### 3. Error Handling
- **Discovery Fails**: `available_tools` defaults to empty dict
- **No Tools Found**: Clear error message about missing tools
- **Connection Issues**: Proper error propagation

## Verification Results

### ✅ All Checks Passed
- `available_tools` attribute initialized in `__init__`
- `_discover_tools` method exists and is called
- Tool discovery makes proper `tools/list` request
- Tools are stored correctly in `available_tools`
- Error handling prevents crashes
- All async methods use `_get_tool_name` properly

## Expected Behavior After Fix

### Repository Indexing
```
INFO: MCP protocol initialized
INFO: Available tools: ['index_repository', 'semantic_search', ...]
INFO: Starting to index repository: https://github.com/user/repo.git
INFO: Using indexing tool: index_repository
✅ Repository indexed successfully
```

### Tool Discovery Logging
```
INFO: Tool: index_repository - Index a repository for semantic search
INFO: Tool: semantic_search - Perform semantic search on repository
INFO: Tool: get_repository_structure - Get repository structure
```

### Graceful Fallback
If tool discovery fails:
```
WARNING: Failed to discover tools: Connection timeout
INFO: Using indexing tool: index_repository (fallback)
```

## Files Modified
- ✅ `mcp_robust_client.py` - Added tool discovery and initialization

## Testing
```bash
# Verify syntax
python -m py_compile mcp_robust_client.py

# Verify fix
python test_available_tools_fix.py
```

## Impact
- **Repository Indexing**: Now works without AttributeError
- **All MCP Tools**: Properly discover and use available tools
- **Better Debugging**: Logs show what tools are available
- **Robust Fallbacks**: Handles tool discovery failures gracefully

The AttributeError should be completely resolved, and repository indexing should work properly now.