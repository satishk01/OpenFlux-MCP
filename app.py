import streamlit as st
import asyncio
import json
import os
from typing import Dict, List, Any, Optional
import boto3
from botocore.exceptions import ClientError
import subprocess
import tempfile
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force reload modules to avoid caching issues
import importlib
import sys

# Clear any cached modules
modules_to_reload = ['mcp_sync_client', 'mcp_client']
for module_name in modules_to_reload:
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])

# Import MCP components
from mcp_robust_client import MCPRobustClient
from bedrock_client import BedrockClient

# Page configuration
st.set_page_config(
    page_title="OpenFlux - MCP Integration Platform",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Kiro-like interface
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .chat-container {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .user-message {
        background-color: #3b82f6;
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        text-align: right;
    }
    
    .assistant-message {
        background-color: #ffffff;
        color: #1f2937;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 80%;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .tool-call {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
    
    .sidebar-section {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-connected {
        background-color: #10b981;
    }
    
    .status-disconnected {
        background-color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)

class OpenFluxApp:
    def __init__(self):
        self.mcp_client = None
        self.bedrock_client = None
        self.last_health_check = 0
        self.health_check_interval = 30  # Check health every 30 seconds
        self.initialize_session_state()
        
    def cleanup(self):
        """Cleanup resources"""
        if self.mcp_client:
            try:
                # Use synchronous cleanup to avoid async issues
                self.mcp_client.cleanup()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            finally:
                self.mcp_client = None
                st.session_state.mcp_connected = False
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'mcp_connected' not in st.session_state:
            st.session_state.mcp_connected = False
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
        if 'github_repo' not in st.session_state:
            st.session_state.github_repo = ''
        if 'aws_region' not in st.session_state:
            st.session_state.aws_region = os.getenv('AWS_REGION', 'us-west-2')
        if 'indexed_repos' not in st.session_state:
            st.session_state.indexed_repos = set()
        if 'last_index_result' not in st.session_state:
            st.session_state.last_index_result = None
        if 'connection_stable' not in st.session_state:
            st.session_state.connection_stable = False
            
    def render_sidebar(self):
        """Render the sidebar with configuration options"""
        with st.sidebar:
            st.markdown('<div class="main-header">🔄 OpenFlux</div>', unsafe_allow_html=True)
            
            # MCP Server Configuration
            with st.container():
                st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                st.subheader("MCP Server Status")
                
                # Check connection health periodically (not every render)
                current_time = time.time()
                is_healthy = st.session_state.connection_stable
                
                if self.mcp_client and st.session_state.mcp_connected:
                    # Only check health every 30 seconds to avoid overwhelming the connection
                    if current_time - self.last_health_check > self.health_check_interval:
                        try:
                            is_healthy = self.mcp_client.check_connection_health()
                            st.session_state.connection_stable = is_healthy
                            self.last_health_check = current_time
                            if not is_healthy:
                                st.session_state.mcp_connected = False
                                logger.warning("Connection health check failed")
                        except Exception as e:
                            logger.error(f"Health check error: {e}")
                            st.session_state.mcp_connected = False
                            st.session_state.connection_stable = False
                else:
                    st.session_state.connection_stable = False
                
                status_color = "status-connected" if is_healthy else "status-disconnected"
                status_text = "Connected & Healthy" if is_healthy else "Disconnected"
                
                st.markdown(f'''
                <div>
                    <span class="status-indicator {status_color}"></span>
                    Git Repo Research Server: {status_text}
                </div>
                ''', unsafe_allow_html=True)
                
                # Show connection details
                if is_healthy and self.mcp_client:
                    st.markdown(f'📚 Indexed repositories: {len(st.session_state.indexed_repos)}')
                    
                    # Show last health check time
                    if hasattr(self, 'last_health_check') and self.last_health_check > 0:
                        time_since_check = int(time.time() - self.last_health_check)
                        st.markdown(f'🕐 Last health check: {time_since_check}s ago')
                
                # Show connection troubleshooting if disconnected
                elif not is_healthy:
                    st.markdown('⚠️ Connection issues detected')
                    st.info("� Don' t worry! I can still help with general programming questions even when repository search isn't available.")
                    if st.button("🔧 Auto-Fix Connection"):
                        with st.spinner("Attempting to fix connection..."):
                            if self.ensure_mcp_connection():
                                st.success("✅ Connection restored!")
                                st.rerun()
                            else:
                                st.error("❌ Auto-fix failed. Try manual reconnection.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reconnect"):
                        self.connect_mcp_server()
                with col2:
                    if st.button("🔌 Disconnect"):
                        self.disconnect_mcp_server()
                    
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Model Selection
            with st.container():
                st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                st.subheader("Model Configuration")
                
                model_options = {
                    'Claude 3.5 Sonnet V2': 'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
                    'Amazon Nova Pro': 'amazon.nova-pro-v1:0'
                }
                
                selected_model_name = st.selectbox(
                    "Select Model",
                    options=list(model_options.keys()),
                    index=0 if st.session_state.selected_model == model_options['Claude 3.5 Sonnet V2'] else 1
                )
                
                st.session_state.selected_model = model_options[selected_model_name]
                
                st.session_state.aws_region = st.selectbox(
                    "AWS Region",
                    options=['us-west-2', 'us-east-1', 'eu-west-1'],
                    index=0
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Repository Configuration
            with st.container():
                st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                st.subheader("Repository Settings")
                
                st.session_state.github_repo = st.text_input(
                    "GitHub Repository",
                    value=st.session_state.github_repo,
                    placeholder="owner/repository-name"
                )
                
                # Show indexing status
                if st.session_state.github_repo:
                    is_indexed = st.session_state.github_repo in st.session_state.indexed_repos
                    if is_indexed:
                        st.success(f"✅ {st.session_state.github_repo} is indexed")
                    else:
                        st.warning(f"⚠️ {st.session_state.github_repo} needs indexing")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔍 Index Repository"):
                        if st.session_state.github_repo:
                            self.index_repository()
                        else:
                            st.error("Please enter a GitHub repository")
                
                with col2:
                    if st.button("📋 Show Indexed"):
                        if st.session_state.indexed_repos:
                            st.info(f"Indexed repos: {', '.join(st.session_state.indexed_repos)}")
                        else:
                            st.info("No repositories indexed yet")
                
                # Show last indexing result
                if st.session_state.last_index_result:
                    with st.expander("Last Index Result"):
                        st.json(st.session_state.last_index_result)
                        
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Environment Status
            with st.container():
                st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                st.subheader("Environment Status")
                
                github_token = os.getenv('GITHUB_TOKEN')
                aws_region = os.getenv('AWS_REGION', 'us-west-2')
                
                if github_token:
                    st.markdown(f'<span class="status-indicator status-connected"></span>GitHub Token: Set', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="status-indicator status-disconnected"></span>GitHub Token: Not Set', unsafe_allow_html=True)
                
                st.markdown(f'<span class="status-indicator status-connected"></span>AWS Region: {aws_region}', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reload Env"):
                        load_dotenv(override=True)
                        st.success("Environment reloaded!")
                        st.rerun()
                with col2:
                    if st.button("🔄 Force Restart"):
                        # Clear session state and force restart
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.success("App restarted!")
                        st.rerun()
                
                # AWS Diagnostics
                if st.button("🔍 AWS Diagnostics"):
                    self.run_aws_diagnostics()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Clear Chat
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
                
    def ensure_mcp_connection(self):
        """Ensure MCP connection is established and healthy"""
        try:
            # If no client exists, create one
            if not self.mcp_client:
                logger.info("Creating new MCP client")
                self.mcp_client = MCPRobustClient()
            
            # If not connected or unhealthy, connect
            if not st.session_state.mcp_connected or not st.session_state.connection_stable:
                logger.info("Establishing MCP connection")
                self.mcp_client.connect()
                st.session_state.mcp_connected = True
                st.session_state.connection_stable = True
                self.last_health_check = time.time()
                return True
            
            # If connected, do a quick health check
            if self.mcp_client.check_connection_health():
                return True
            else:
                logger.warning("Connection unhealthy, reconnecting")
                self.mcp_client.connect()
                st.session_state.mcp_connected = True
                st.session_state.connection_stable = True
                self.last_health_check = time.time()
                return True
                
        except Exception as e:
            logger.error(f"Failed to ensure MCP connection: {e}")
            st.session_state.mcp_connected = False
            st.session_state.connection_stable = False
            return False
    
    def connect_mcp_server(self):
        """Connect to the MCP server with better error handling"""
        try:
            with st.spinner("Connecting to MCP server..."):
                # Cleanup existing client if any
                if self.mcp_client:
                    try:
                        self.mcp_client.cleanup()
                    except:
                        pass
                
                # Create new client and connect
                self.mcp_client = MCPRobustClient()
                logger.info(f"Created MCP client: {type(self.mcp_client)}")
                self.mcp_client.connect()
                
                # Mark as connected and stable
                st.session_state.mcp_connected = True
                st.session_state.connection_stable = True
                self.last_health_check = time.time()
                
                st.success("✅ MCP server connected successfully!")
                logger.info("MCP server connected successfully")
                
        except Exception as e:
            error_msg = str(e)
            st.error("Failed to connect to MCP server")
            
            # Show detailed error in expandable section
            with st.expander("🔍 Connection Error Details", expanded=True):
                st.code(error_msg, language="text")
                
                # Provide setup instructions based on error type
                if "uvx command not found" in error_msg or "uv" in error_msg.lower():
                    st.markdown("""
                    ### 🛠️ Setup Required: Install uv/uvx
                    
                    The MCP server requires `uvx` to run. Please install it:
                    
                    **Option 1: Using pip**
                    ```bash
                    pip install uv
                    ```
                    
                    **Option 2: Using the installer**
                    Visit: https://docs.astral.sh/uv/getting-started/installation/
                    
                    After installation, restart the application.
                    """)
                    
                elif "GITHUB_TOKEN" in error_msg:
                    st.markdown("""
                    ### 🔑 Setup Required: GitHub Token
                    
                    You need a GitHub Personal Access Token to access repositories:
                    
                    1. **Create a token**: Go to https://github.com/settings/tokens
                    2. **Set permissions**: Select "repo" scope for private repos, or "public_repo" for public repos
                    3. **Copy the token** and add it to your `.env` file:
                       ```
                       GITHUB_TOKEN=your_actual_token_here
                       ```
                    4. **Restart** the application
                    """)
                    
                else:
                    st.markdown("""
                    ### 🔧 Troubleshooting Tips
                    
                    1. **Check Prerequisites**: Make sure `uv` and `uvx` are installed
                    2. **Verify Environment**: Check your `.env` file has the correct values
                    3. **Restart Application**: Try restarting after making changes
                    4. **Check Logs**: Look at the console output for more details
                    """)
            
            st.session_state.mcp_connected = False
            st.session_state.connection_stable = False
            if self.mcp_client:
                try:
                    self.mcp_client.cleanup()
                except:
                    pass
            self.mcp_client = None
            
    def disconnect_mcp_server(self):
        """Disconnect from the MCP server"""
        try:
            if self.mcp_client:
                with st.spinner("Disconnecting from MCP server..."):
                    self.mcp_client.disconnect()
                    self.mcp_client = None
                    st.session_state.mcp_connected = False
                    st.success("MCP server disconnected successfully!")
            else:
                st.info("MCP server is not connected")
        except Exception as e:
            st.error(f"Error disconnecting from MCP server: {str(e)}")
            # Force cleanup even if disconnect fails
            self.cleanup()
            
    def run_aws_diagnostics(self):
        """Run AWS diagnostics to help debug credential issues"""
        try:
            from aws_utils import test_aws_credentials, test_bedrock_access, get_ec2_instance_metadata, clear_aws_env_credentials, restore_aws_env_credentials
            
            with st.spinner("Running AWS diagnostics..."):
                # Check EC2 metadata
                ec2_info = get_ec2_instance_metadata()
                
                if ec2_info["is_ec2"]:
                    st.success(f"✅ Running on EC2 instance: {ec2_info['instance_id']}")
                    if ec2_info["iam_role"]:
                        st.info(f"📋 IAM Role: {ec2_info['iam_role']}")
                    else:
                        st.warning("⚠️ No IAM role attached to EC2 instance")
                else:
                    st.info("ℹ️ Not running on EC2 instance")
                
                # Test current credentials
                st.write("**Testing current AWS credentials:**")
                cred_test = test_aws_credentials(st.session_state.aws_region)
                
                if cred_test["success"]:
                    st.success(f"✅ AWS credentials working - Method: {cred_test['method']}")
                    st.info(f"Account: {cred_test['account']}")
                else:
                    st.error(f"❌ AWS credentials failed: {cred_test['error']}")
                
                # Test Bedrock access
                st.write("**Testing Bedrock access:**")
                bedrock_test = test_bedrock_access(st.session_state.aws_region)
                
                if bedrock_test["success"]:
                    st.success(f"✅ Bedrock access working - {bedrock_test['models_available']} models available")
                    if bedrock_test["claude_available"]:
                        st.info("✅ Claude models available")
                    if bedrock_test["nova_available"]:
                        st.info("✅ Nova models available")
                else:
                    st.error(f"❌ Bedrock access failed: {bedrock_test['error']}")
                    
                    # If on EC2, try clearing env vars to force instance role
                    if ec2_info["is_ec2"] and ec2_info["iam_role"]:
                        st.write("**Trying with instance role only:**")
                        
                        # Clear environment credentials temporarily
                        saved_creds = clear_aws_env_credentials()
                        
                        try:
                            bedrock_test_role = test_bedrock_access(st.session_state.aws_region)
                            if bedrock_test_role["success"]:
                                st.success("✅ Bedrock works with instance role!")
                                st.info("💡 Suggestion: Remove AWS credentials from environment variables")
                            else:
                                st.error(f"❌ Instance role also failed: {bedrock_test_role['error']}")
                        finally:
                            # Restore credentials
                            restore_aws_env_credentials(saved_creds)
                
        except Exception as e:
            st.error(f"Diagnostics failed: {str(e)}")
            
    def index_repository(self):
        """Index the specified GitHub repository with better feedback"""
        repo = st.session_state.github_repo
        
        try:
            # Ensure connection is healthy before indexing
            if not self.ensure_mcp_connection():
                st.error("❌ Failed to establish MCP connection")
                return
            
            with st.spinner(f"Indexing repository {repo}... This may take a few minutes for large repositories."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔍 Starting repository indexing...")
                progress_bar.progress(10)
                
                logger.info(f"Starting to index repository: {repo}")
                
                # Index with retry logic
                max_retries = 1  # Only one retry for indexing (it's a longer operation)
                result = None
                
                for attempt in range(max_retries + 1):
                    try:
                        result = self.mcp_client.index_repository(repo)
                        break  # Success, exit retry loop
                    except Exception as e:
                        logger.warning(f"Index attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries:
                            logger.info(f"Retrying indexing (attempt {attempt + 2}/{max_retries + 1})")
                            if not self.ensure_mcp_connection():
                                raise Exception("Failed to reconnect for retry")
                            time.sleep(2)  # Longer pause for indexing retry
                        else:
                            raise  # Final attempt failed, re-raise the exception
                
                if result is None:
                    raise Exception("Indexing failed after all retry attempts")
                
                progress_bar.progress(80)
                status_text.text("✅ Processing indexing results...")
                
                # Store the result and mark as indexed
                st.session_state.last_index_result = result
                st.session_state.indexed_repos.add(repo)
                
                progress_bar.progress(100)
                status_text.text("🎉 Indexing completed!")
                
                # Show success with details
                st.success(f"✅ Repository '{repo}' indexed successfully!")
                
                # Show indexing statistics if available
                if isinstance(result, dict):
                    if 'indexed_files' in result:
                        st.info(f"📁 Indexed {result['indexed_files']} files")
                    if 'total_chunks' in result:
                        st.info(f"🔍 Created {result['total_chunks']} searchable chunks")
                    if 'status' in result:
                        st.info(f"📊 Status: {result['status']}")
                
                logger.info(f"Successfully indexed repository: {repo}")
                logger.info(f"Index result: {result}")
                
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Failed to index repository: {error_msg}")
            
            # Provide specific guidance based on error
            if "not connected" in error_msg.lower():
                st.warning("🔌 MCP server connection lost. Please reconnect and try again.")
            elif "timeout" in error_msg.lower():
                st.warning("⏱️ Indexing timed out. Try with a smaller repository or check your connection.")
            elif "github" in error_msg.lower() and "token" in error_msg.lower():
                st.warning("🔑 GitHub token issue. Check your token permissions.")
            elif "not found" in error_msg.lower():
                st.warning("🔍 Repository not found. Check the repository name and your access permissions.")
            elif "unknown tool" in error_msg.lower() or "no indexing tool found" in error_msg.lower():
                st.warning("🔧 The MCP server doesn't have the required indexing tools available. Please check your MCP server configuration and ensure it supports repository indexing.")
            
            logger.error(f"Index error for {repo}: {e}", exc_info=True)
            
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.markdown('<div class="main-header">Chat with OpenFlux</div>', unsafe_allow_html=True)
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                elif message["role"] == "assistant":
                    st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
                elif message["role"] == "tool":
                    st.markdown(f'<div class="tool-call"><strong>Tool Call:</strong> {message["name"]}<br><pre>{message["content"]}</pre></div>', unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Ask about your repository or search for code..."):
            self.handle_user_input(prompt)
            
    def handle_user_input(self, prompt: str):
        """Handle user input and generate response"""
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        try:
            # Initialize Bedrock client if not exists
            if not self.bedrock_client:
                self.bedrock_client = BedrockClient(
                    region=st.session_state.aws_region,
                    model_id=st.session_state.selected_model
                )
            
            # Enhanced query detection for repository searches
            search_keywords = [
                'search', 'find', 'look for', 'show me', 'where is', 'how does',
                'code', 'function', 'class', 'method', 'variable', 'file',
                'implementation', 'algorithm', 'pattern', 'example',
                'api', 'endpoint', 'route', 'handler', 'controller',
                'test', 'spec', 'config', 'setup', 'init',
                'error', 'exception', 'bug', 'issue',
                'import', 'export', 'module', 'package',
                'database', 'model', 'schema', 'query',
                'authentication', 'auth', 'login', 'user',
                'component', 'service', 'util', 'helper'
            ]
            
            # Check if we have a repository and if this looks like a code search
            has_repo = bool(st.session_state.github_repo)
            is_search_query = any(keyword in prompt.lower() for keyword in search_keywords)
            
            if has_repo and is_search_query:
                # Use fallback mechanism for repository searches
                self.handle_query_with_fallback(prompt, st.session_state.github_repo)
            elif has_repo and not is_search_query:
                # Ask user if they want to search the repository
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"I can search the repository '{st.session_state.github_repo}' for information related to your question. Would you like me to search the codebase, or would you prefer a general response?"
                })
                # For now, default to general query, but user can rephrase to trigger search
                self.handle_general_query(prompt)
            else:
                self.handle_general_query(prompt)
                
        except Exception as e:
            st.error(f"Error processing request: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"I encountered an error: {str(e)}"
            })
        
        st.rerun()
        
    def handle_repository_search(self, query: str):
        """Handle repository search queries with automatic connection management"""
        repo = st.session_state.github_repo
        
        # Ensure MCP connection is healthy before proceeding
        if not self.ensure_mcp_connection():
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🔌 Failed to establish MCP server connection. Please check your setup and try reconnecting manually."
            })
            return
            
        if not repo:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "📁 Please specify a GitHub repository to search in the sidebar."
            })
            return
        
        # Check if repository is indexed
        if repo not in st.session_state.indexed_repos:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Repository '{repo}' has not been indexed yet. Please index it first using the 'Index Repository' button in the sidebar."
            })
            return
            
        try:
            with st.spinner("🔍 Searching repository..."):
                # Perform semantic search using MCP with retry logic
                max_retries = 2
                search_results = None
                
                for attempt in range(max_retries + 1):
                    try:
                        search_results = self.mcp_client.semantic_search(
                            repository=repo,
                            query=query,
                            max_results=15  # Get more results for better context
                        )
                        break  # Success, exit retry loop
                    except Exception as e:
                        logger.warning(f"Search attempt {attempt + 1} failed: {e}")
                        if attempt < max_retries:
                            # Try to reconnect and retry
                            logger.info(f"Retrying search (attempt {attempt + 2}/{max_retries + 1})")
                            if not self.ensure_mcp_connection():
                                raise Exception("Failed to reconnect for retry")
                            time.sleep(1)  # Brief pause before retry
                        else:
                            raise  # Final attempt failed, re-raise the exception
                
                if search_results is None:
                    raise Exception("Search failed after all retry attempts")
                
                # Check if search results contain an error
                if isinstance(search_results, dict):
                    # Check for error in the response
                    if search_results.get('isError', False) or 'error' in search_results:
                        error_content = search_results.get('content', [])
                        if error_content and isinstance(error_content, list) and len(error_content) > 0:
                            error_text = error_content[0].get('text', 'Unknown error')
                            if "unknown tool" in error_text.lower():
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": f"🔧 I'm having trouble accessing the search functionality. The MCP server doesn't recognize the search tool.\n\n**What this means:** The repository search feature isn't available right now.\n\n**What you can do:**\n• Ask me general programming questions\n• Try reconnecting to the MCP server\n• Check your MCP server configuration\n\n**Your question was:** '{query}' - I'd be happy to help with general information about this topic!"
                                })
                                return
                            else:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": f"❌ Search error: {error_text}\n\nPlease try reconnecting or ask me a general question instead."
                                })
                                return
                
                # Add tool call message with better formatting (only if no error)
                tool_content = f"Search Query: {query}\nRepository: {repo}\nResults: {json.dumps(search_results, indent=2)}"
                st.session_state.messages.append({
                    "role": "tool",
                    "name": "semantic_search",
                    "content": tool_content
                })
                
                # Check if we got meaningful results
                results = search_results.get('results', []) if isinstance(search_results, dict) else []
                
                if not results:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🔍 No results found for '{query}' in repository '{repo}'.\n\n**Suggestions:**\n• Try different keywords or phrases\n• Use more general terms (e.g., 'authentication' instead of 'auth middleware')\n• Check if the repository contains the type of content you're looking for\n• Make sure the repository has been properly indexed\n\n**Alternative:** Ask me a general question about '{query}' and I'll help with concepts and best practices!"
                    })
                    return
                
                # Generate response using Bedrock with better context
                context = f"""Repository: {repo}
Search Query: {query}
Number of Results: {len(results)}

Search Results:
{json.dumps(search_results, indent=2)}

Please analyze these search results and provide a helpful response about the code found."""
                
                response = self.bedrock_client.generate_response(
                    f"Based on the search results, please help me understand: {query}", 
                    context
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                logger.info(f"Search completed for '{query}' in {repo}, found {len(results)} results")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Search error for '{query}' in {repo}: {e}", exc_info=True)
            
            # Provide specific error guidance
            if "not indexed" in error_msg.lower():
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"📚 Repository '{repo}' needs to be indexed first. Please use the 'Index Repository' button in the sidebar."
                })
            elif "not connected" in error_msg.lower() or "unhealthy" in error_msg.lower():
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "🔌 MCP server connection lost. Please reconnect using the sidebar and try again."
                })
            elif "timeout" in error_msg.lower():
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⏱️ Search timed out. Please try again with a more specific query."
                })
            elif "unknown tool" in error_msg.lower() or "no search tool found" in error_msg.lower():
                # Handle MCP tool not available error
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"🔧 I'm having trouble accessing the search functionality. The MCP server doesn't seem to have the expected search tools available.\n\n**What you can try:**\n1. Check if the MCP server is properly configured\n2. Try reconnecting using the sidebar\n3. Verify your MCP server supports semantic search\n\n**Alternative:** You can ask me general questions about programming concepts, and I'll help without needing to search the repository."
                })
            elif "no results found" in error_msg.lower() or "empty results" in error_msg.lower():
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"🔍 No results found for '{query}' in repository '{repo}'.\n\n**Suggestions:**\n• Try different keywords or phrases\n• Use more general terms\n• Check if the repository contains the type of content you're looking for\n• Make sure the repository has been properly indexed"
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ I encountered an issue while searching: {error_msg}\n\n**What you can try:**\n• Check your connection and try again\n• Try reconnecting to the MCP server\n• Use different search terms\n• Ask me a general question instead"
                })
            
    def handle_general_query(self, query: str):
        """Handle general queries using Bedrock"""
        try:
            with st.spinner("Generating response..."):
                response = self.bedrock_client.generate_response(query)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
        except Exception as e:
            
    def handle_query_with_fallback(self, query: str, repo: str = None):
        """Handle queries with fallback to general responses when MCP fails"""
        # First try MCP search if repository is specified
        if repo and repo in st.session_state.indexed_repos:
            try:
                self.handle_repository_search(query)
                return
            except Exception as e:
                logger.warning(f"MCP search failed, falling back to general response: {e}")
                
                # Add a note about the fallback
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"🔄 I couldn't search the repository directly, but I can still help with your question about: '{query}'\n\nLet me provide general guidance:"
                })
        
        # Fallback to general query
        enhanced_query = query
        if repo:
            enhanced_query = f"Regarding the GitHub repository '{repo}', {query}. Please provide general guidance and best practices."
        
        self.handle_general_query(enhanced_query)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Failed to generate response: {str(e)}"
            })
            
    def run(self):
        """Main application entry point"""
        # Auto-connect MCP server on first load or if connection is lost
        if not st.session_state.mcp_connected and not hasattr(st.session_state, 'connection_attempted'):
            st.session_state.connection_attempted = True
            with st.spinner("🔄 Initializing MCP connection..."):
                self.ensure_mcp_connection()
        
        self.render_sidebar()
        self.render_chat_interface()
        
        # Periodic connection maintenance (every 5 minutes)
        if hasattr(st.session_state, 'last_maintenance'):
            if time.time() - st.session_state.last_maintenance > 300:  # 5 minutes
                if self.mcp_client and st.session_state.mcp_connected:
                    try:
                        # Quick health check and maintenance
                        if not self.mcp_client.check_connection_health():
                            logger.info("Performing connection maintenance")
                            self.ensure_mcp_connection()
                    except Exception as e:
                        logger.error(f"Connection maintenance error: {e}")
                st.session_state.last_maintenance = time.time()
        else:
            st.session_state.last_maintenance = time.time()

def main():
    app = OpenFluxApp()
    
    # Register cleanup on app shutdown
    import atexit
    atexit.register(app.cleanup)
    
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        app.cleanup()
    except Exception as e:
        logger.error(f"Application error: {e}")
        app.cleanup()
        raise

if __name__ == "__main__":
    main()