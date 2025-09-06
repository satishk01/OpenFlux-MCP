"""
Synchronous MCP Client for Streamlit
This client avoids asyncio event loop conflicts by running all async operations
in a dedicated thread with its own event loop.
"""

import json
import subprocess
import os
import logging
import threading
import asyncio
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MCPSyncClient:
    """Synchronous MCP client that avoids event loop conflicts"""
    
    def __init__(self):
        self.process = None
        self.connected = False
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mcp-client")
        self.loop = None
        self.loop_thread = None
        self.server_config = {
            "command": "uvx",
            "args": ["awslabs.git-repo-research-mcp-server@latest"],
            "env": {
                "AWS_PROFILE": os.getenv("AWS_PROFILE", "default"),
                "AWS_REGION": os.getenv("AWS_REGION", "us-west-2"),
                "FASTMCP_LOG_LEVEL": "ERROR",
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
            }
        }
        
    def _run_in_thread(self, coro):
        """Run a coroutine in the dedicated thread"""
        def run_async():
            if self.loop is None or self.loop.is_closed():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            
            try:
                return self.loop.run_until_complete(coro)
            except Exception as e:
                logger.error(f"Error in async operation: {e}")
                raise
        
        future = self.executor.submit(run_async)
        return future.result(timeout=60)  # 60 second timeout
        
    async def _connect_async(self):
        """Async connection logic"""
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
            
            # Wait a moment for the process to start
            await asyncio.sleep(3)
            
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
        
        await self._send_request(init_request)
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        await self._send_request(initialized_notification)
        
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response"""
        if not self.process:
            raise Exception("MCP server not connected")
            
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response if expecting one
        if "id" in request:
            response_line = await self.process.stdout.readline()
            if response_line:
                return json.loads(response_line.decode().strip())
        
        return {}
        
    async def _index_repository_async(self, repository: str) -> Dict[str, Any]:
        """Async repository indexing"""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "index_repository",
                "arguments": {
                    "repository": repository
                }
            }
        }
        
        response = await self._send_request(request)
        return response.get("result", {})
        
    async def _semantic_search_async(self, repository: str, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Async semantic search"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "semantic_search",
                "arguments": {
                    "repository": repository,
                    "query": query,
                    "max_results": max_results
                }
            }
        }
        
        response = await self._send_request(request)
        return response.get("result", {})
        
    async def _disconnect_async(self):
        """Async disconnection"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
            self.connected = False
            logger.info("MCP server disconnected")
            
    # Public synchronous methods
    def connect(self):
        """Connect to the MCP server (synchronous)"""
        return self._run_in_thread(self._connect_async())
        
    def disconnect(self):
        """Disconnect from the MCP server (synchronous)"""
        if self.connected:
            return self._run_in_thread(self._disconnect_async())
        
    def index_repository(self, repository: str) -> Dict[str, Any]:
        """Index a repository for semantic search (synchronous)"""
        if not self.connected:
            raise Exception("MCP server not connected")
        return self._run_in_thread(self._index_repository_async(repository))
        
    def semantic_search(self, repository: str, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform semantic search on a repository (synchronous)"""
        if not self.connected:
            raise Exception("MCP server not connected")
        return self._run_in_thread(self._semantic_search_async(repository, query, max_results))
        
    def cleanup(self):
        """Synchronous cleanup"""
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                # Give it a moment to terminate gracefully
                time.sleep(1)
                if self.process.returncode is None:
                    self.process.kill()
            except Exception as e:
                logger.error(f"Error during process cleanup: {e}")
            finally:
                self.process = None
                self.connected = False
                
        # Cleanup thread pool
        if self.executor:
            self.executor.shutdown(wait=False)
            
        # Cleanup event loop
        if self.loop and not self.loop.is_closed():
            try:
                # Schedule loop closure in the thread
                def close_loop():
                    if self.loop and not self.loop.is_closed():
                        self.loop.call_soon_threadsafe(self.loop.stop)
                
                threading.Thread(target=close_loop, daemon=True).start()
            except Exception as e:
                logger.error(f"Error closing event loop: {e}")
                
        logger.info("MCP client cleanup completed")
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup()