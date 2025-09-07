# Error Handling Improvements

## Overview
This document outlines the improvements made to handle MCP tool failures and provide better user experience when repository search functionality is unavailable.

## Problem Addressed
Users were receiving confusing raw error messages like:
```json
{
  "content": [
    {
      "type": "text", 
      "text": "Unknown tool: semantic_search"
    }
  ],
  "isError": true
}
```

## Improvements Implemented

### 1. Enhanced Error Detection
- **Better Error Parsing**: Now properly detects error responses from MCP server
- **Specific Error Types**: Identifies different types of errors (unknown tool, timeout, connection issues)
- **Error Response Validation**: Checks for `isError` flag and error content in responses

### 2. User-Friendly Error Messages

#### Unknown Tool Errors
Instead of raw JSON, users now see:
```
🔧 I'm having trouble accessing the search functionality. The MCP server doesn't recognize the search tool.

What this means: The repository search feature isn't available right now.

What you can do:
• Ask me general programming questions
• Try reconnecting to the MCP server  
• Check your MCP server configuration

Your question was: 'What are the files in pysrc folder' - I'd be happy to help with general information about this topic!
```

#### No Results Found
```
🔍 No results found for 'your query' in repository 'repo-name'.

Suggestions:
• Try different keywords or phrases
• Use more general terms (e.g., 'authentication' instead of 'auth middleware')
• Check if the repository contains the type of content you're looking for
• Make sure the repository has been properly indexed

Alternative: Ask me a general question about 'your query' and I'll help with concepts and best practices!
```

#### Connection Issues
```
🔌 MCP server connection lost. Please reconnect using the sidebar and try again.
```

#### Timeout Errors
```
⏱️ Search timed out. Please try again with a more specific query.
```

### 3. Fallback Mechanism
- **Automatic Fallback**: When MCP search fails, automatically falls back to general responses
- **Context Preservation**: Maintains the user's original question context
- **Enhanced Queries**: Enriches general queries with repository context when available

### 4. Improved Indexing Error Handling
- **Tool Availability Check**: Detects when indexing tools are not available
- **Specific Guidance**: Provides targeted help based on error type
- **Configuration Hints**: Suggests checking MCP server configuration

### 5. Sidebar Improvements
- **Status Indicators**: Shows connection health and available tools
- **Helpful Messages**: Informs users about fallback capabilities
- **Tool Discovery**: Option to view available MCP tools

## Code Changes Made

### app.py
1. **Enhanced Search Error Handling** (lines ~780-820)
   - Added detection for "unknown tool" errors
   - Improved error message formatting
   - Added fallback suggestions

2. **Search Result Validation** (lines ~740-760)
   - Checks for error flags in MCP responses
   - Validates response structure before processing
   - Handles malformed responses gracefully

3. **Fallback Query Handler** (new method)
   - `handle_query_with_fallback()` - Tries MCP first, falls back to general responses
   - Preserves user context in fallback scenarios
   - Provides seamless user experience

4. **Indexing Error Improvements** (lines ~600-620)
   - Added "unknown tool" detection for indexing
   - Better error categorization
   - Helpful configuration guidance

5. **Sidebar Status Updates** (lines ~200-220)
   - Added reassuring message about fallback capabilities
   - Better connection status indicators

## User Experience Improvements

### Before
- Raw JSON error messages
- Confusing technical errors
- No guidance on what to do next
- Users left stuck when MCP fails

### After
- Clear, friendly error messages
- Specific suggestions for each error type
- Automatic fallback to general help
- Users can always get assistance

## Testing
Created `test_error_handling.py` to verify:
- Error response parsing works correctly
- Different error types are handled appropriately
- Fallback mechanisms function as expected
- User-friendly messages are generated

## Benefits
1. **Better User Experience**: Users never hit dead ends
2. **Reduced Confusion**: Clear explanations instead of technical errors
3. **Increased Reliability**: App remains useful even when MCP fails
4. **Better Support**: Users get helpful guidance for troubleshooting
5. **Graceful Degradation**: Seamless fallback to general assistance

## Future Enhancements
- Add retry mechanisms with exponential backoff
- Implement caching for frequently asked questions
- Add more sophisticated error recovery strategies
- Provide more detailed MCP server diagnostics