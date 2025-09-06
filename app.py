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
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import MCP components
from mcp_client import MCPClient
from bedrock_client import BedrockClient
from async_handler import run_async

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
            st.session_state.selected_model = 'anthropic.claude-3-5-sonnet-20241022-v2:0'
        if 'github_repo' not in st.session_state:
            st.session_state.github_repo = ''
        if 'aws_region' not in st.session_state:
            st.session_state.aws_region = os.getenv('AWS_REGION', 'us-west-2')
            
    def render_sidebar(self):
        """Render the sidebar with configuration options"""
        with st.sidebar:
            st.markdown('<div class="main-header">🔄 OpenFlux</div>', unsafe_allow_html=True)
            
            # MCP Server Configuration
            with st.container():
                st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
                st.subheader("MCP Server Status")
                
                status_color = "status-connected" if st.session_state.mcp_connected else "status-disconnected"
                status_text = "Connected" if st.session_state.mcp_connected else "Disconnected"
                
                st.markdown(f'''
                <div>
                    <span class="status-indicator {status_color}"></span>
                    Git Repo Research Server: {status_text}
                </div>
                ''', unsafe_allow_html=True)
                
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
                    'Claude 3.5 Sonnet V2': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
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
                
                if st.button("🔍 Index Repository"):
                    if st.session_state.github_repo:
                        self.index_repository()
                    else:
                        st.error("Please enter a GitHub repository")
                        
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
                
                if st.button("🔄 Reload Environment"):
                    load_dotenv(override=True)
                    st.success("Environment reloaded!")
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Clear Chat
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
                
    def connect_mcp_server(self):
        """Connect to the MCP server"""
        try:
            with st.spinner("Connecting to MCP server..."):
                # Disconnect existing client if any
                if self.mcp_client:
                    try:
                        run_async(self.mcp_client.disconnect())
                    except:
                        pass
                
                self.mcp_client = MCPClient()
                run_async(self.mcp_client.connect())
                st.session_state.mcp_connected = True
                st.success("MCP server connected successfully!")
        except Exception as e:
            st.error(f"Failed to connect to MCP server: {str(e)}")
            st.session_state.mcp_connected = False
            self.mcp_client = None
            
    def disconnect_mcp_server(self):
        """Disconnect from the MCP server"""
        try:
            if self.mcp_client:
                with st.spinner("Disconnecting from MCP server..."):
                    run_async(self.mcp_client.disconnect())
                    self.mcp_client = None
                    st.session_state.mcp_connected = False
                    st.success("MCP server disconnected successfully!")
            else:
                st.info("MCP server is not connected")
        except Exception as e:
            st.error(f"Error disconnecting from MCP server: {str(e)}")
            # Force cleanup even if disconnect fails
            self.cleanup()
            
    def index_repository(self):
        """Index the specified GitHub repository"""
        try:
            with st.spinner(f"Indexing repository {st.session_state.github_repo}..."):
                if not self.mcp_client:
                    self.connect_mcp_server()
                
                if self.mcp_client:
                    result = run_async(self.mcp_client.index_repository(st.session_state.github_repo))
                    st.success(f"Repository {st.session_state.github_repo} indexed successfully!")
                else:
                    st.error("MCP client not connected")
        except Exception as e:
            st.error(f"Failed to index repository: {str(e)}")
            
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
            
            # Check if this is a repository search query
            if any(keyword in prompt.lower() for keyword in ['search', 'find', 'look for', 'code', 'function', 'class']):
                self.handle_repository_search(prompt)
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
        """Handle repository search queries"""
        if not st.session_state.mcp_connected or not self.mcp_client:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "MCP server is not connected. Please connect to the server first."
            })
            return
            
        if not st.session_state.github_repo:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Please specify a GitHub repository to search."
            })
            return
            
        try:
            with st.spinner("Searching repository..."):
                # Perform semantic search using MCP
                search_results = run_async(
                    self.mcp_client.semantic_search(
                        repository=st.session_state.github_repo,
                        query=query
                    )
                )
                
                # Add tool call message
                st.session_state.messages.append({
                    "role": "tool",
                    "name": "semantic_search",
                    "content": json.dumps(search_results, indent=2)
                })
                
                # Generate response using Bedrock
                context = f"Repository: {st.session_state.github_repo}\nSearch Results: {json.dumps(search_results, indent=2)}"
                response = self.bedrock_client.generate_response(query, context)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Search failed: {str(e)}"
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
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Failed to generate response: {str(e)}"
            })
            
    def run(self):
        """Main application entry point"""
        self.render_sidebar()
        self.render_chat_interface()
        
        # Auto-connect MCP server on first load
        if not st.session_state.mcp_connected and not hasattr(st.session_state, 'connection_attempted'):
            st.session_state.connection_attempted = True
            self.connect_mcp_server()

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