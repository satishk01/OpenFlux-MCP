"""
Robust MCP Client for Streamlit
This client provides better connection stability, error handling, and feedback
"""

import json
import subprocess
import os
import logging
import threading
import asyncio
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
from dotenv import load_dotenv
import signal

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MCPRobustClient:
    """Robust MCP client with better stability and error handling"""
    
    def __init__(self):
        self.process = None
        self.connected = False
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mcp-robust")
        self.loop = None
        self.loop_thread = None
        self.connection_lock = threading.Lock()
        self.last_activity = time.time()
        self.indexed_repositories = set()  # Track indexed repos
        self.server_config = {
            "command": "uvx",
            "args": ["awslabs.git-repo-research-mcp-server@latest"],
            "env": {
                "AWS_PROFILE": os.getenv("AWS_PROFILE", "default"),
                "AWS_REGION": os.getenv("AWS_REGION", "us-west-2"),
                "FASTMCP_LOG_LEVEL": "INFO",  # More verbose for debugging
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
            }
        }
        
    def _run_in_thread(self, coro, timeout=120):
        """Run a coroutine in the dedicated thread with timeout"""
        def run_async():
            if self.loop is None or self.loop.is_closed():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            try:
                return self.loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
            except asyncio.TimeoutError:
                logger.error(f"Operation timed out after {timeout} seconds")
                raise TimeoutError(f"MCP operation timed out after {timeout} seconds")
            except Exception as e:
                logger.error(f"Error in async operation: {e}")
                raise
        
        future = self.executor.submit(run_async)
        try:
            return future.result(timeout=timeout + 10)  # Extra buffer for thread overhead
        except TimeoutError:
            logger.error("Thread execution timed out")
            raise TimeoutError("MCP client operation timed out")
        
    def is_process_alive(self):
        """Check if the MCP server process is still alive"""
        if not self.process:
            return False
        return self.process.returncode is None
        
    def check_connection_health(self):
        """Check if the connection is healthy"""
        with self.connection_lock:
            if not self.connected:
                return False
            
            if not self.is_process_alive():
                logger.warning("MCP server process died, marking as disconnected")
                self.connected = False
                return False
            
            # Check if we've been inactive for too long
            if time.time() - self.last_activity > 300:  # 5 minutes
                logger.info("Connection has been inactive, testing health")
                try:
                    # Try a simple ping-like operation
                    self._run_in_thread(self._health_check_async(), timeout=10)
                    self.last_activity = time.time()
                    return True
                except Exception as e:
                    logger.warning(f"Health check failed: {e}")
                    self.connected = False
                    return False
            
            return True
        
    async def _health_check_async(self):
        """Simple health check for the MCP server"""
        if not self.process:
            raise Exception("No process")
        
        # Just check if we can write to stdin without error
        try:
            # Send a simple request that should always work
            request = {
                "jsonrpc": "2.0",
                "id": 999,
                "method": "ping"  # This might not be implemented, but that's ok
            }
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Don't wait for response since ping might not be implemented
            # The fact that we could write means the connection is alive
            return True
        except Exception as e:
            logger.error(f"Health check write failed: {e}")
            raise
        
    async def _connect_async(self):
        """Async connection logic with better error handling"""
        try:
            # Check if uvx is available
            try:
                proc = await asyncio.create_subprocess_exec(
                    "uvx", "--version",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.wait()
                if proc.returncode != 0:
                    raise FileNotFoundError()
            except FileNotFoundError:
                raise Exception(
                    "uvx command not found. Please install uv first:\n"
                    "1. Visit: https://docs.astral.sh/uv/getting-started/installation/\n"
                    "2. Or run: pip install uv\n"
                    "3. Then restart the application"
                )
            
            # Validate environment
            github_token = self.server_config["env"]["GITHUB_TOKEN"]
            if not github_token:
                raise Exception(
                    "GITHUB_TOKEN environment variable is required.\n"
                    "1. Create a GitHub Personal Access Token at: https://github.com/settings/tokens\n"
                    "2. Set it in your .env file: GITHUB_TOKEN=your_token_here\n"
                    "3. Restart the application"
                )
            
            if github_token == "your-github-token":
                raise Exception(
                    "Please replace 'your-github-token' with your actual GitHub token in the .env file.\n"
                    "1. Get a token from: https://github.com/settings/tokens\n"
                    "2. Update .env file: GITHUB_TOKEN=your_actual_token\n"
                    "3. Restart the application"
                )
                
            logger.info(f"Using GitHub token: {github_token[:8]}...")
            logger.info(f"AWS Region: {self.server_config['env']['AWS_REGION']}")
            logger.info(f"AWS Profile: {self.server_config['env']['AWS_PROFILE']}")
            
            # Start the MCP server process
            env = os.environ.copy()
            env.update(self.server_config["env"])
            
            logger.info(f"Starting MCP server: {self.server_config['command']} {' '.join(self.server_config['args'])}")
            
            self.process = await asyncio.create_subprocess_exec(
                self.server_config["command"],
                *self.server_config["args"],
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait longer for the process to start
            await asyncio.sleep(5)
            
            # Check if process is still running
            if self.process.returncode is not None:
                stderr_output = await self.process.stderr.read()
                stdout_output = await self.process.stdout.read()
                error_msg = stderr_output.decode() if stderr_output else "Unknown error"
                stdout_msg = stdout_output.decode() if stdout_output else ""
                
                full_error = f"MCP server process failed to start (exit code: {self.process.returncode})\n"
                if error_msg:
                    full_error += f"Error: {error_msg}\n"
                if stdout_msg:
                    full_error += f"Output: {stdout_msg}\n"
                
                # Common error handling
                if "command not found" in error_msg.lower() or "not found" in error_msg.lower():
                    full_error += "\nSolution: Install uv/uvx:\n"
                    full_error += "1. Visit: https://docs.astral.sh/uv/getting-started/installation/\n"
                    full_error += "2. Or run: pip install uv"
                elif "permission denied" in error_msg.lower():
                    full_error += "\nSolution: Check file permissions and try running as administrator"
                elif "github" in error_msg.lower() and "token" in error_msg.lower():
                    full_error += "\nSolution: Check your GitHub token is valid and has proper permissions"
                
                raise Exception(full_error)
            
            # Initialize MCP protocol
            await self._initialize_protocol()
            self.connected = True
            self.last_activity = time.time()
            logger.info("MCP server connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.connected = False
            raise
            
    async def _initialize_protocol(self):
        """Initialize the MCP protocol with the server"""
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "OpenFlux",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(init_request)
        logger.info(f"Initialize response: {response}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        await self._send_request(initialized_notification)
        logger.info("MCP protocol initialized")
        
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response"""
        if not self.process:
            raise Exception("MCP server not connected")
            
        request_json = json.dumps(request) + "\n"
        logger.debug(f"Sending request: {request_json.strip()}")
        
        try:
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            self.last_activity = time.time()
        except Exception as e:
            logger.error(f"Failed to send request: {e}")
            self.connected = False
            raise Exception(f"Failed to send request to MCP server: {e}")
        
        # Read response if expecting one
        if "id" in request:
            try:
                response_line = await asyncio.wait_for(
                    self.process.stdout.readline(), 
                    timeout=30  # 30 second timeout for responses
                )
                if response_line:
                    response_text = response_line.decode().strip()
                    logger.debug(f"Received response: {response_text}")
                    return json.loads(response_text)
                else:
                    raise Exception("No response received from MCP server")
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for MCP server response")
                raise Exception("Timeout waiting for MCP server response")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {e}")
                raise Exception(f"Invalid response from MCP server: {e}")
        
        return {}
        
    def _get_tool_name(self, preferred_names: List[str]) -> Optional[str]:
        """Get the actual tool name from a list of preferred names"""
        for name in preferred_names:
            if name in self.available_tools:
                return name
        return None
        
    async def _index_repository_async(self, repository: str) -> Dict[str, Any]:
        """Async repository indexing with better feedback"""
        logger.info(f"Starting to index repository: {repository}")
        
        # Try different possible tool names for indexing
        index_tool_name = self._get_tool_name([
            "index_repository",
            "index-repository", 
            "index_repo",
            "index-repo",
            "repository_index",
            "repo_index",
            "clone_and_index",
            "clone-and-index"
        ])
        
        if not index_tool_name:
            available_names = list(self.available_tools.keys())
            raise Exception(f"No indexing tool found. Available tools: {available_names}")
        
        logger.info(f"Using indexing tool: {index_tool_name}")
        
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),  # Use timestamp as unique ID
            "method": "tools/call",
            "params": {
                "name": index_tool_name,
                "arguments": {
                    "repository": repository
                }
            }
        }
        
        response = await self._send_request(request)
        
        # Check for errors in response
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            logger.error(f"Index repository error: {error_msg}")
            raise Exception(f"Failed to index repository: {error_msg}")
        
        result = response.get("result", {})
        logger.info(f"Index repository result: {result}")
        
        # Mark repository as indexed
        self.indexed_repositories.add(repository)
        
        return result
        
    async def _semantic_search_async(self, repository: str, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Async semantic search with better error handling"""
        logger.info(f"Performing semantic search on {repository} for: {query}")
        
        # Try different possible tool names for searching
        search_tool_name = self._get_tool_name([
            "semantic_search",
            "semantic-search",
            "search",
            "search_repository", 
            "search-repository",
            "repo_search",
            "repo-search",
            "query",
            "find",
            "search_code",
            "search-code"
        ])
        
        if not search_tool_name:
            available_names = list(self.available_tools.keys())
            raise Exception(f"No search tool found. Available tools: {available_names}")
        
        logger.info(f"Using search tool: {search_tool_name}")
        
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),  # Use timestamp as unique ID
            "method": "tools/call",
            "params": {
                "name": search_tool_name,
                "arguments": {
                    "repository": repository,
                    "query": query,
                    "max_results": max_results
                }
            }
        }
        
        response = await self._send_request(request)
        
        # Check for errors in response
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            logger.error(f"Semantic search error: {error_msg}")
            
            # If repository not indexed, suggest indexing
            if "not indexed" in error_msg.lower() or "index" in error_msg.lower():
                raise Exception(f"Repository '{repository}' may not be indexed. Please index it first using the 'Index Repository' button.")
            
            raise Exception(f"Search failed: {error_msg}")
        
        result = response.get("result", {})
        logger.info(f"Search returned {len(result.get('results', []))} results")
        
        return result
        
    async def _disconnect_async(self):
        """Async disconnection with proper cleanup"""
        if self.process:
            try:
                # Try graceful termination first
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                # Force kill if graceful termination fails
                logger.warning("Graceful termination timed out, force killing process")
                self.process.kill()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error during process termination: {e}")
                try:
                    self.process.kill()
                    await self.process.wait()
                except:
                    pass
            finally:
                self.process = None
                self.connected = False
                self.indexed_repositories.clear()
                logger.info("MCP server disconnected")
            
    # Public synchronous methods
    def connect(self):
        """Connect to the MCP server (synchronous)"""
        with self.connection_lock:
            if self.connected and self.check_connection_health():
                logger.info("Already connected and healthy")
                return
            
            logger.info("Establishing new MCP connection")
            return self._run_in_thread(self._connect_async())
        
    def disconnect(self):
        """Disconnect from the MCP server (synchronous)"""
        with self.connection_lock:
            if self.connected:
                return self._run_in_thread(self._disconnect_async())
        
    def index_repository(self, repository: str) -> Dict[str, Any]:
        """Index a repository for semantic search (synchronous)"""
        if not self.check_connection_health():
            raise Exception("MCP server not connected or unhealthy. Please reconnect.")
        
        try:
            return self._run_in_thread(self._index_repository_async(repository))
        except Exception as e:
            # If connection failed during operation, mark as disconnected
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                self.connected = False
            raise
        
    def semantic_search(self, repository: str, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform semantic search on a repository (synchronous)"""
        if not self.check_connection_health():
            raise Exception("MCP server not connected or unhealthy. Please reconnect.")
        
        try:
            return self._run_in_thread(self._semantic_search_async(repository, query, max_results))
        except Exception as e:
            # If connection failed during operation, mark as disconnected
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                self.connected = False
            raise
        
    def is_repository_indexed(self, repository: str) -> bool:
        """Check if a repository has been indexed"""
        return repository in self.indexed_repositories
        
    async def _get_file_content_async(self, repository: str, file_path: str) -> Dict[str, Any]:
        """Async get file content with better error handling"""
        logger.info(f"Getting file content from {repository}: {file_path}")
        
        # Try different possible tool names for file access
        file_tool_name = self._get_tool_name([
            "get_file_content",
            "get-file-content",
            "file_content",
            "file-content",
            "read_file",
            "read-file",
            "get_file",
            "get-file"
        ])
        
        if not file_tool_name:
            available_names = list(self.available_tools.keys())
            raise Exception(f"No file access tool found. Available tools: {available_names}")
        
        logger.info(f"Using file access tool: {file_tool_name}")
        
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": file_tool_name,
                "arguments": {
                    "repository": repository,
                    "file_path": file_path
                }
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            logger.error(f"Get file content error: {error_msg}")
            raise Exception(f"Failed to get file content: {error_msg}")
        
        result = response.get("result", {})
        logger.info(f"File content retrieved successfully")
        
        return result
        
    async def _get_repository_structure_async(self, repository: str) -> Dict[str, Any]:
        """Async get repository structure with better error handling"""
        logger.info(f"Getting repository structure for: {repository}")
        
        # Try different possible tool names for repository structure
        structure_tool_name = self._get_tool_name([
            "get_repository_structure",
            "get-repository-structure",
            "repository_structure",
            "repository-structure",
            "repo_structure",
            "repo-structure",
            "list_files",
            "list-files",
            "tree"
        ])
        
        if not structure_tool_name:
            available_names = list(self.available_tools.keys())
            raise Exception(f"No repository structure tool found. Available tools: {available_names}")
        
        logger.info(f"Using repository structure tool: {structure_tool_name}")
        
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": structure_tool_name,
                "arguments": {
                    "repository": repository
                }
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            logger.error(f"Get repository structure error: {error_msg}")
            raise Exception(f"Failed to get repository structure: {error_msg}")
        
        result = response.get("result", {})
        logger.info(f"Repository structure retrieved successfully")
        
        return result
        
    async def _search_code_async(self, repository: str, pattern: str, file_type: str = None) -> Dict[str, Any]:
        """Async code search with better error handling"""
        logger.info(f"Searching code in {repository} for pattern: {pattern}")
        
        # Try different possible tool names for code search
        code_search_tool_name = self._get_tool_name([
            "search_code",
            "search-code",
            "code_search",
            "code-search",
            "grep",
            "find_code",
            "find-code",
            "pattern_search",
            "pattern-search"
        ])
        
        if not code_search_tool_name:
            available_names = list(self.available_tools.keys())
            raise Exception(f"No code search tool found. Available tools: {available_names}")
        
        logger.info(f"Using code search tool: {code_search_tool_name}")
        
        arguments = {
            "repository": repository,
            "pattern": pattern
        }
        
        if file_type:
            arguments["file_type"] = file_type
        
        request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": code_search_tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            logger.error(f"Code search error: {error_msg}")
            raise Exception(f"Failed to search code: {error_msg}")
        
        result = response.get("result", {})
        logger.info(f"Code search completed, found results")
        
        return result
        
    def get_file_content(self, repository: str, file_path: str) -> Dict[str, Any]:
        """Get content of a specific file from repository (synchronous)"""
        if not self.check_connection_health():
            raise Exception("MCP server not connected or unhealthy")
        
        try:
            return self._run_in_thread(self._get_file_content_async(repository, file_path))
        except Exception as e:
            if not self.check_connection_health():
                self.connected = False
            raise
            
    def get_repository_structure(self, repository: str) -> Dict[str, Any]:
        """Get the structure of a repository (synchronous)"""
        if not self.check_connection_health():
            raise Exception("MCP server not connected or unhealthy")
        
        try:
            return self._run_in_thread(self._get_repository_structure_async(repository))
        except Exception as e:
            if not self.check_connection_health():
                self.connected = False
            raise
            
    def search_code(self, repository: str, pattern: str, file_type: str = None) -> Dict[str, Any]:
        """Search for code patterns in repository (synchronous)"""
        if not self.check_connection_health():
            raise Exception("MCP server not connected or unhealthy")
        
        try:
            return self._run_in_thread(self._search_code_async(repository, pattern, file_type))
        except Exception as e:
            if not self.check_connection_health():
                self.connected = False
            raise
        
    def get_indexed_repositories(self) -> List[str]:
        """Get list of indexed repositories"""
        return list(self.indexed_repositories)
        
    def cleanup(self):
        """Synchronous cleanup with better error handling"""
        logger.info("Starting MCP client cleanup")
        
        with self.connection_lock:
            if self.process and self.process.returncode is None:
                try:
                    self.process.terminate()
                    # Give it a moment to terminate gracefully
                    time.sleep(2)
                    if self.process.returncode is None:
                        logger.warning("Process didn't terminate gracefully, force killing")
                        self.process.kill()
                        time.sleep(1)
                except Exception as e:
                    logger.error(f"Error during process cleanup: {e}")
                finally:
                    self.process = None
                    self.connected = False
                    self.indexed_repositories.clear()
                    
            # Cleanup thread pool
            if self.executor:
                try:
                    self.executor.shutdown(wait=True, timeout=5)
                except Exception as e:
                    logger.error(f"Error shutting down executor: {e}")
                    
            # Cleanup event loop
            if self.loop and not self.loop.is_closed():
                try:
                    # Schedule loop closure in the thread
                    def close_loop():
                        if self.loop and not self.loop.is_closed():
                            try:
                                self.loop.call_soon_threadsafe(self.loop.stop)
                            except:
                                pass
                    
                    threading.Thread(target=close_loop, daemon=True).start()
                    time.sleep(1)  # Give it time to close
                except Exception as e:
                    logger.error(f"Error closing event loop: {e}")
                    
        logger.info("MCP client cleanup completed")
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors during destruction