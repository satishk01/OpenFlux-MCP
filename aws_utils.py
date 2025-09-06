"""
AWS utilities for credential management
"""

import os
import boto3
import logging
from typing import Dict, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def clear_aws_env_credentials():
    """Clear AWS credentials from environment variables to force instance role usage"""
    env_vars_to_clear = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
    cleared_vars = {}
    
    for var in env_vars_to_clear:
        if var in os.environ:
            cleared_vars[var] = os.environ[var]
            del os.environ[var]
            logger.info(f"Cleared environment variable: {var}")
    
    return cleared_vars

def restore_aws_env_credentials(credentials: Dict[str, str]):
    """Restore AWS credentials to environment variables"""
    for var, value in credentials.items():
        os.environ[var] = value
        logger.info(f"Restored environment variable: {var}")

def test_aws_credentials(region: str = "us-east-1") -> Dict[str, any]:
    """Test AWS credentials and return status"""
    result = {
        "success": False,
        "method": None,
        "error": None,
        "account": None,
        "user_arn": None
    }
    
    try:
        # Create session and test credentials
        session = boto3.Session()
        sts_client = session.client('sts', region_name=region)
        
        # Get caller identity
        identity = sts_client.get_caller_identity()
        
        result["success"] = True
        result["account"] = identity.get("Account")
        result["user_arn"] = identity.get("Arn")
        
        # Determine credential method
        credentials = session.get_credentials()
        if credentials:
            result["method"] = credentials.method
        
        logger.info(f"AWS credentials test successful: {result['method']}")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"AWS credentials test failed: {e}")
    
    return result

def test_bedrock_access(region: str = "us-east-1") -> Dict[str, any]:
    """Test Bedrock access specifically"""
    result = {
        "success": False,
        "error": None,
        "models_available": 0,
        "claude_available": False,
        "nova_available": False
    }
    
    try:
        # Test basic AWS credentials first
        cred_test = test_aws_credentials(region)
        if not cred_test["success"]:
            result["error"] = f"AWS credentials failed: {cred_test['error']}"
            return result
        
        # Test Bedrock access
        session = boto3.Session()
        bedrock_client = session.client('bedrock', region_name=region)
        
        # List foundation models
        models_response = bedrock_client.list_foundation_models()
        models = models_response.get('modelSummaries', [])
        
        result["success"] = True
        result["models_available"] = len(models)
        
        # Check for specific models
        for model in models:
            model_id = model.get('modelId', '')
            if 'claude' in model_id.lower():
                result["claude_available"] = True
            if 'nova' in model_id.lower():
                result["nova_available"] = True
        
        logger.info(f"Bedrock access test successful: {result['models_available']} models available")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Bedrock access test failed: {e}")
    
    return result

def get_ec2_instance_metadata() -> Dict[str, any]:
    """Get EC2 instance metadata to verify we're running on EC2"""
    result = {
        "is_ec2": False,
        "instance_id": None,
        "region": None,
        "iam_role": None,
        "error": None
    }
    
    try:
        import requests
        
        # EC2 metadata endpoint
        metadata_url = "http://169.254.169.254/latest/meta-data/"
        
        # Test if we can reach the metadata service
        response = requests.get(metadata_url, timeout=2)
        if response.status_code == 200:
            result["is_ec2"] = True
            
            # Get instance ID
            try:
                instance_id_response = requests.get(f"{metadata_url}instance-id", timeout=2)
                if instance_id_response.status_code == 200:
                    result["instance_id"] = instance_id_response.text
            except:
                pass
            
            # Get region
            try:
                region_response = requests.get(f"{metadata_url}placement/region", timeout=2)
                if region_response.status_code == 200:
                    result["region"] = region_response.text
            except:
                pass
            
            # Get IAM role
            try:
                iam_response = requests.get(f"{metadata_url}iam/security-credentials/", timeout=2)
                if iam_response.status_code == 200:
                    result["iam_role"] = iam_response.text.strip()
            except:
                pass
        
        logger.info(f"EC2 metadata check: {result}")
        
    except Exception as e:
        result["error"] = str(e)
        logger.warning(f"EC2 metadata check failed: {e}")
    
    return result