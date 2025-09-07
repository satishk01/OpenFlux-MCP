# MCP Tools Summary

## Overview
The OpenFlux application now supports **5 different types of MCP tools** for comprehensive repository analysis and code exploration.

## Supported MCP Tools

### 1. 🔍 **Semantic Search** (`semantic_search`)
- **Purpose**: Natural language search through repository content
- **Usage**: Find code, functions, concepts using plain English
- **Example Queries**:
  - "Find authentication functions"
  - "Show me error handling code"
  - "Where is the database connection logic?"
- **Tool Variations Supported**: `semantic_search`, `semantic-search`, `search`, `search_repository`, `query`

### 2. 📚 **Repository Indexing** (`index_repository`) 
- **Purpose**: Index repository content for semantic search
- **Usage**: Prepare repository for searchable analysis
- **Example**: Automatically triggered when indexing repositories
- **Tool Variations Supported**: `index_repository`, `index-repository`, `index_repo`, `clone_and_index`

### 3. 📁 **Repository Structure** (`get_repository_structure`)
- **Purpose**: Get directory structure and project organization
- **Usage**: Understand project layout and architecture
- **Example Queries**:
  - "Show me the repository structure"
  - "What's the project organization?"
  - "Display the directory tree"
- **Tool Variations Supported**: `get_repository_structure`, `repository_structure`, `repo_structure`, `tree`

### 4. 📄 **File Content Access** (`get_file_content`)
- **Purpose**: Retrieve content of specific files
- **Usage**: View and analyze individual files
- **Example Queries**:
  - "Show me the file src/main.py"
  - "Get file README.md"
  - "Display contents of config.json"
- **Tool Variations Supported**: `get_file_content`, `file_content`, `read_file`, `get_file`

### 5. 🔎 **Code Pattern Search** (`search_code`)
- **Purpose**: Search for specific code patterns or text matches
- **Usage**: Find exact patterns, regex matches, or text occurrences
- **Example Queries**:
  - "Search for pattern 'function main'"
  - "Find 'class User'"
  - "Look for 'import React'"
- **Tool Variations Supported**: `search_code`, `code_search`, `grep`, `find_code`, `pattern_search`

## Query Detection & Routing

The app automatically detects what type of operation you want based on keywords:

### Search Keywords
`search`, `find`, `look for`, `show me`, `where is`, `how does`, `code`, `function`, `class`, `method`, `implementation`, `algorithm`, `pattern`, `example`, `api`, `endpoint`, `test`, `config`, `error`, `import`, `database`, `authentication`, `component`, `service`

### File Keywords  
`file`, `show file`, `get file`, `read file`, `file content`, `open file`, `view file`, `display file`, `contents of`

### Structure Keywords
`structure`, `organization`, `layout`, `directories`, `folders`, `tree`, `hierarchy`, `files and folders`, `project structure`, `repository structure`, `directory tree`

### Pattern Keywords
`pattern`, `regex`, `grep`, `match`, `contains`, `code pattern`, `search pattern`, `find pattern`

## Error Handling & Fallbacks

### Smart Tool Discovery
- Automatically discovers what tools are available from the MCP server
- Tries multiple tool name variations (e.g., `semantic_search`, `semantic-search`, `search`)
- Provides clear error messages when tools aren't available

### Graceful Fallbacks
- When MCP tools fail, automatically falls back to general programming assistance
- Preserves user's original question context
- Ensures users always get helpful responses

### User-Friendly Error Messages
Instead of raw JSON errors, users see helpful messages like:
```
🔧 I'm having trouble accessing the search functionality. The MCP server doesn't recognize the search tool.

What this means: The repository search feature isn't available right now.

What you can do:
• Ask me general programming questions
• Try reconnecting to the MCP server
• Check your MCP server configuration

Your question was: 'Find authentication functions' - I'd be happy to help with general information about this topic!
```

## Usage Examples

### Repository Structure
**User**: "Show me the repository structure"
**App**: Uses `get_repository_structure` → Displays organized directory tree with analysis

### File Content
**User**: "Show me the file src/components/Header.js"  
**App**: Uses `get_file_content` → Displays file content with code analysis

### Semantic Search
**User**: "Find authentication functions"
**App**: Uses `semantic_search` → Finds relevant code with context

### Pattern Search  
**User**: "Search for pattern 'useState'"
**App**: Uses `search_code` → Finds exact pattern matches

### Fallback Example
**User**: "Find database connections" (when MCP fails)
**App**: "🔄 I couldn't search the repository directly, but I can still help with your question about database connections. Let me provide general guidance..."

## Benefits

1. **Comprehensive Coverage**: 5 different ways to explore repositories
2. **Smart Detection**: Automatically routes queries to appropriate tools
3. **Robust Fallbacks**: Never leaves users stuck when tools fail
4. **User-Friendly**: Clear, helpful messages instead of technical errors
5. **Flexible Tool Support**: Works with different MCP server implementations

## Technical Implementation

- **Tool Name Mapping**: Supports multiple naming conventions for each tool
- **Connection Health**: Monitors MCP server health and reconnects as needed
- **Async Operations**: Non-blocking tool calls with proper error handling
- **Context Preservation**: Maintains conversation context through tool failures
- **Response Validation**: Checks tool responses before processing

This comprehensive MCP tool support makes OpenFlux a powerful platform for repository analysis and code exploration, with robust fallbacks ensuring a smooth user experience even when individual tools aren't available.