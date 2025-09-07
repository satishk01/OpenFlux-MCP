#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for indexing issues
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("=" * 40)
    
    required_vars = [
        'GITHUB_TOKEN',
        'AWS_PROFILE', 
        'AWS_REGION',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY'
    ]
    
    issues = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'KEY' in var:
                masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            issues.append(var)
    
    return len(issues) == 0, issues

def check_aws_credentials():
    """Check AWS credentials and Bedrock access"""
    print("\n🔍 Checking AWS Credentials")
    print("=" * 40)
    
    try:
        # Try to run AWS CLI command
        result = subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print(f"✅ AWS Identity: {identity.get('Arn', 'Unknown')}")
            print(f"✅ Account: {identity.get('Account', 'Unknown')}")
            return True
        else:
            print(f"❌ AWS CLI Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ AWS CLI timeout - check network connectivity")
        return False
    except FileNotFoundError:
        print("❌ AWS CLI not found - install AWS CLI")
        return False
    except Exception as e:
        print(f"❌ AWS CLI Error: {e}")
        return False

def check_bedrock_access():
    """Check Amazon Bedrock access"""
    print("\n🔍 Checking Amazon Bedrock Access")
    print("=" * 40)
    
    try:
        # Try to list Bedrock models
        result = subprocess.run([
            'aws', 'bedrock', 'list-foundation-models', 
            '--region', os.getenv('AWS_REGION', 'us-west-2')
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            models = json.loads(result.stdout)
            model_count = len(models.get('modelSummaries', []))
            print(f"✅ Bedrock accessible - {model_count} models available")
            
            # Check for embedding models
            embedding_models = [m for m in models.get('modelSummaries', []) 
                              if 'embed' in m.get('modelId', '').lower()]
            if embedding_models:
                print(f"✅ Embedding models available: {len(embedding_models)}")
                for model in embedding_models[:3]:  # Show first 3
                    print(f"   • {model.get('modelId')}")
            else:
                print("⚠️  No embedding models found")
            
            return True
        else:
            print(f"❌ Bedrock Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Bedrock timeout - check network/permissions")
        return False
    except Exception as e:
        print(f"❌ Bedrock Error: {e}")
        return False

def check_github_token():
    """Check GitHub token validity"""
    print("\n🔍 Checking GitHub Token")
    print("=" * 40)
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN not set")
        return False
    
    try:
        import requests
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Test token with user info
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token valid for user: {user_info.get('login')}")
            
            # Check rate limit
            rate_limit = response.headers.get('X-RateLimit-Remaining')
            print(f"✅ Rate limit remaining: {rate_limit}")
            
            # Test repository access
            repo_response = requests.get(
                'https://api.github.com/repos/satishk01/data-formulator',
                headers=headers, timeout=10
            )
            
            if repo_response.status_code == 200:
                print("✅ Repository accessible")
                return True
            elif repo_response.status_code == 404:
                print("❌ Repository not found or no access")
                return False
            else:
                print(f"⚠️  Repository access issue: {repo_response.status_code}")
                return False
                
        else:
            print(f"❌ Token invalid: {response.status_code} - {response.text}")
            return False
            
    except ImportError:
        print("❌ requests module not available")
        return False
    except Exception as e:
        print(f"❌ GitHub API Error: {e}")
        return False

def check_mcp_server_status():
    """Check if MCP server process is running"""
    print("\n🔍 Checking MCP Server Status")
    print("=" * 40)
    
    try:
        # Check for uvx processes (MCP server typically runs via uvx)
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            mcp_processes = [line for line in lines if 'uvx' in line or 'mcp' in line.lower()]
            
            if mcp_processes:
                print(f"✅ Found {len(mcp_processes)} MCP-related processes")
                for proc in mcp_processes[:3]:  # Show first 3
                    print(f"   • {proc.strip()}")
                return True
            else:
                print("❌ No MCP server processes found")
                return False
        else:
            print("❌ Cannot check processes")
            return False
            
    except Exception as e:
        print(f"❌ Process check error: {e}")
        return False

def check_file_system():
    """Check file system permissions and space"""
    print("\n🔍 Checking File System")
    print("=" * 40)
    
    # Check if the git_repo_research directory exists
    research_dir = Path("/home/ec2-user/.git_repo_research")
    
    if research_dir.exists():
        print(f"✅ Research directory exists: {research_dir}")
        
        # Check permissions
        if os.access(research_dir, os.W_OK):
            print("✅ Directory is writable")
        else:
            print("❌ Directory is not writable")
            return False
            
        # Check contents
        try:
            contents = list(research_dir.iterdir())
            print(f"✅ Directory contents: {len(contents)} items")
            for item in contents[:5]:  # Show first 5
                print(f"   • {item.name}")
        except Exception as e:
            print(f"❌ Cannot list directory: {e}")
            return False
            
    else:
        print(f"⚠️  Research directory doesn't exist: {research_dir}")
        
        # Try to create it
        try:
            research_dir.mkdir(parents=True, exist_ok=True)
            print("✅ Created research directory")
        except Exception as e:
            print(f"❌ Cannot create directory: {e}")
            return False
    
    # Check disk space
    try:
        stat = os.statvfs(research_dir.parent)
        free_space = stat.f_bavail * stat.f_frsize
        free_gb = free_space / (1024**3)
        print(f"✅ Free disk space: {free_gb:.1f} GB")
        
        if free_gb < 1:
            print("⚠️  Low disk space - may cause indexing issues")
            
    except Exception as e:
        print(f"⚠️  Cannot check disk space: {e}")
    
    return True

def suggest_fixes(issues):
    """Suggest fixes based on identified issues"""
    print("\n🔧 Suggested Fixes")
    print("=" * 30)
    
    if 'GITHUB_TOKEN' in issues:
        print("\n1. **Set GitHub Token:**")
        print("   export GITHUB_TOKEN=your_token_here")
        print("   # Or add to .env file")
    
    if any('AWS' in issue for issue in issues):
        print("\n2. **Configure AWS Credentials:**")
        print("   aws configure")
        print("   # Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    
    print("\n3. **Test with Simple Repository:**")
    print("   Try: https://github.com/octocat/Hello-World.git")
    
    print("\n4. **Check MCP Server Logs:**")
    print("   Look for detailed error messages in application logs")
    
    print("\n5. **Restart MCP Server:**")
    print("   Restart your application to reinitialize MCP connection")

def main():
    """Main diagnostic function"""
    print("🔧 Indexing Issue Diagnostic Tool")
    print("=" * 60)
    
    all_issues = []
    
    # Run all checks
    env_ok, env_issues = check_environment_variables()
    if not env_ok:
        all_issues.extend(env_issues)
    
    aws_ok = check_aws_credentials()
    if not aws_ok:
        all_issues.append('AWS_CREDENTIALS')
    
    bedrock_ok = check_bedrock_access()
    if not bedrock_ok:
        all_issues.append('BEDROCK_ACCESS')
    
    github_ok = check_github_token()
    if not github_ok:
        all_issues.append('GITHUB_ACCESS')
    
    mcp_ok = check_mcp_server_status()
    if not mcp_ok:
        all_issues.append('MCP_SERVER')
    
    fs_ok = check_file_system()
    if not fs_ok:
        all_issues.append('FILE_SYSTEM')
    
    # Summary
    print("\n" + "=" * 60)
    
    if not all_issues:
        print("🎉 All checks passed!")
        print("\n✅ Environment appears to be configured correctly.")
        print("✅ The indexing issue may be in the application logic.")
        print("\n🔍 Next steps:")
        print("   • Check application logs for detailed errors")
        print("   • Try indexing a simple public repository")
        print("   • Verify MCP server is receiving requests")
    else:
        print(f"❌ Found {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"   • {issue}")
        
        suggest_fixes(all_issues)
    
    return len(all_issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)