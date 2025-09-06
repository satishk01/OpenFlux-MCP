import asyncio
import json
import subprocess
import tempfile
import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with MCP servers"""
    
    def __init__(self):
        self.process = None
        self.connected = False
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
        
    async def connect(self):
        """Connect to the MCP server"""
        try:
            # Validate environment
            if not self.server_config["env"]["GITHUB_TOKEN"]:
                raise Exception("GITHUB_TOKEN environment variable is required")
                
            # Start the MCP server process
            env = os.environ.copy()
            env.update(self.server_config["env"])
            
            self.process = await asyncio.create_subprocess_exec(
                self.server_config["command"],
                *self.server_config["args"],
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
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
        
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await self._send_request(request)
        return response.get("result", {}).get("tools", [])
        
    async def semantic_search(self, repository: str, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform semantic search on a repository"""
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
        
    async def index_repository(self, repository: str) -> Dict[str, Any]:
        """Index a repository for semantic search"""
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
        
    async def get_file_content(self, repository: str, file_path: str) -> Dict[str, Any]:
        """Get content of a specific file from repository"""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_file_content",
                "arguments": {
                    "repository": repository,
                    "file_path": file_path
                }
            }
        }
        
        response = await self._send_request(request)
        return response.get("result", {})
        
    async def search_code(self, repository: str, pattern: str, file_type: str = None) -> Dict[str, Any]:
        """Search for code patterns in repository"""
        arguments = {
            "repository": repository,
            "pattern": pattern
        }
        
        if file_type:
            arguments["file_type"] = file_type
            
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "search_code",
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        return response.get("result", {})
        
    async def get_repository_structure(self, repository: str) -> Dict[str, Any]:
        """Get the structure of a repository"""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "get_repository_structure",
                "arguments": {
                    "repository": repository
                }
            }
        }
        
        response = await self._send_request(request)
        return response.get("result", {})
        
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
            self.connected = False
            logger.info("MCP server disconnected")
            
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.process and not self.process.returncode:
            try:
                asyncio.create_task(self.disconnect())
            except:
                pass