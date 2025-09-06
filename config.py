import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration management for OpenFlux"""
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
    AWS_PROFILE = os.getenv("AWS_PROFILE", "default")
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    
    # Streamlit Configuration
    STREAMLIT_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_HOST = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    
    # MCP Server Configuration
    MCP_SERVER_CONFIG = {
        "awslabs.git-repo-research-mcp-server": {
            "command": "uvx",
            "args": ["awslabs.git-repo-research-mcp-server@latest"],
            "env": {
                "AWS_PROFILE": AWS_PROFILE,
                "AWS_REGION": AWS_REGION,
                "FASTMCP_LOG_LEVEL": os.getenv("FASTMCP_LOG_LEVEL", "ERROR"),
                "GITHUB_TOKEN": GITHUB_TOKEN
            },
            "disabled": False,
            "autoApprove": []
        }
    }
    
    # Bedrock Model Configuration
    BEDROCK_MODELS = {
        "claude-3.5-sonnet-v2": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        "amazon-nova-pro": "amazon.nova-pro-v1:0"
    }
    
    DEFAULT_MODEL = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not cls.GITHUB_TOKEN:
            issues.append("GITHUB_TOKEN is not set")
            
        # Check AWS credentials (basic check)
        try:
            import boto3
            session = boto3.Session(profile_name=cls.AWS_PROFILE)
            credentials = session.get_credentials()
            if not credentials:
                issues.append("AWS credentials not found")
        except Exception as e:
            issues.append(f"AWS configuration error: {str(e)}")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "aws_region": cls.AWS_REGION,
                "aws_profile": cls.AWS_PROFILE,
                "github_token_set": bool(cls.GITHUB_TOKEN),
                "default_model": cls.DEFAULT_MODEL
            }
        }