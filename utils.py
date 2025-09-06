import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st

logger = logging.getLogger(__name__)

def format_timestamp() -> str:
    """Format current timestamp for logging"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def safe_json_loads(json_str: str) -> Dict[str, Any]:
    """Safely load JSON string with error handling"""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return {"error": f"Invalid JSON: {str(e)}"}

def format_search_results(results: Dict[str, Any]) -> str:
    """Format search results for display"""
    if not results or "error" in results:
        return "No results found or error occurred."
    
    formatted = []
    
    if "matches" in results:
        for i, match in enumerate(results["matches"][:5], 1):  # Limit to top 5
            file_path = match.get("file_path", "Unknown file")
            score = match.get("score", 0)
            content = match.get("content", "")[:200] + "..." if len(match.get("content", "")) > 200 else match.get("content", "")
            
            formatted.append(f"""
**Match {i}** (Score: {score:.3f})
- **File:** `{file_path}`
- **Content:** {content}
""")
    
    return "\n".join(formatted) if formatted else "No matches found."

def format_code_snippet(code: str, language: str = "python") -> str:
    """Format code snippet for display"""
    return f"```{language}\n{code}\n```"

def extract_repository_info(repo_url: str) -> Dict[str, str]:
    """Extract owner and repo name from GitHub URL or repo string"""
    if repo_url.startswith("https://github.com/"):
        repo_url = repo_url.replace("https://github.com/", "")
    
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    
    parts = repo_url.split("/")
    if len(parts) >= 2:
        return {
            "owner": parts[0],
            "repo": parts[1],
            "full_name": f"{parts[0]}/{parts[1]}"
        }
    
    return {"owner": "", "repo": "", "full_name": repo_url}

def validate_github_repo(repo_string: str) -> bool:
    """Validate GitHub repository string format"""
    if not repo_string:
        return False
    
    info = extract_repository_info(repo_string)
    return bool(info["owner"] and info["repo"])

def create_error_message(error: Exception, context: str = "") -> str:
    """Create formatted error message"""
    timestamp = format_timestamp()
    context_str = f" ({context})" if context else ""
    return f"[{timestamp}] Error{context_str}: {str(error)}"

def log_mcp_interaction(method: str, params: Dict[str, Any], response: Dict[str, Any]):
    """Log MCP server interactions for debugging"""
    logger.debug(f"MCP {method} - Params: {json.dumps(params, indent=2)}")
    logger.debug(f"MCP {method} - Response: {json.dumps(response, indent=2)}")

class StreamlitLogger:
    """Custom logger for Streamlit applications"""
    
    @staticmethod
    def info(message: str):
        st.info(f"ℹ️ {message}")
        logger.info(message)
    
    @staticmethod
    def success(message: str):
        st.success(f"✅ {message}")
        logger.info(message)
    
    @staticmethod
    def warning(message: str):
        st.warning(f"⚠️ {message}")
        logger.warning(message)
    
    @staticmethod
    def error(message: str):
        st.error(f"❌ {message}")
        logger.error(message)

def run_async_in_streamlit(coro):
    """Run async function in Streamlit context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

def format_file_tree(structure: Dict[str, Any], prefix: str = "") -> str:
    """Format repository structure as a tree"""
    if not structure:
        return "No structure data available"
    
    lines = []
    
    def add_items(items, current_prefix):
        if isinstance(items, dict):
            for key, value in items.items():
                if isinstance(value, dict):
                    lines.append(f"{current_prefix}📁 {key}/")
                    add_items(value, current_prefix + "  ")
                else:
                    lines.append(f"{current_prefix}📄 {key}")
        elif isinstance(items, list):
            for item in items:
                if isinstance(item, str):
                    lines.append(f"{current_prefix}📄 {item}")
                else:
                    lines.append(f"{current_prefix}📁 {str(item)}")
    
    add_items(structure, prefix)
    return "\n".join(lines[:50])  # Limit to 50 lines

def parse_search_query(query: str) -> Dict[str, Any]:
    """Parse search query to extract intent and parameters"""
    query_lower = query.lower()
    
    intent = "general"
    file_types = []
    keywords = []
    
    # Detect search intent
    if any(word in query_lower for word in ["function", "method", "def ", "func"]):
        intent = "function_search"
    elif any(word in query_lower for word in ["class", "interface", "struct"]):
        intent = "class_search"
    elif any(word in query_lower for word in ["import", "require", "include"]):
        intent = "import_search"
    elif any(word in query_lower for word in ["config", "setting", "env"]):
        intent = "config_search"
    elif any(word in query_lower for word in ["test", "spec", "unittest"]):
        intent = "test_search"
    
    # Extract file types
    file_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".rb", ".php"]
    for ext in file_extensions:
        if ext in query_lower:
            file_types.append(ext[1:])  # Remove the dot
    
    # Extract keywords (simple approach)
    words = query.split()
    keywords = [word.strip(".,!?;:") for word in words if len(word) > 2]
    
    return {
        "intent": intent,
        "file_types": file_types,
        "keywords": keywords,
        "original_query": query
    }