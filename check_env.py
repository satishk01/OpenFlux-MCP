#!/usr/bin/env python3
"""
Environment checker for OpenFlux
Run this to verify your environment variables are loaded correctly
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def check_env_file():
    """Check if .env file exists and is readable"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create one by copying .env.example:")
        print("   cp .env.example .env")
        return False
    
    print("✅ .env file found")
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            print(f"✅ .env file is readable ({len(content)} characters)")
            
            # Show non-sensitive parts
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0] if '=' in line else line
                    print(f"   Found variable: {key}")
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    return True

def load_and_check_env():
    """Load environment variables and check critical ones"""
    print("\n🔄 Loading environment variables...")
    
    # Load from .env file
    load_dotenv(override=True)
    print("✅ Environment variables loaded")
    
    # Check critical variables
    variables = {
        'GITHUB_TOKEN': 'GitHub API access',
        'AWS_REGION': 'AWS region for Bedrock',
        'AWS_PROFILE': 'AWS profile (optional)',
        'AWS_ACCESS_KEY_ID': 'AWS access key (optional)',
        'AWS_SECRET_ACCESS_KEY': 'AWS secret key (optional)'
    }
    
    print("\n📋 Environment Variable Status:")
    all_good = True
    
    for var_name, description in variables.items():
        value = os.getenv(var_name)
        if value:
            if 'TOKEN' in var_name or 'KEY' in var_name:
                # Mask sensitive values
                masked_value = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var_name}: {masked_value} ({description})")
            else:
                print(f"✅ {var_name}: {value} ({description})")
        else:
            if var_name in ['GITHUB_TOKEN']:
                print(f"❌ {var_name}: Not set ({description}) - REQUIRED")
                all_good = False
            else:
                print(f"⚠️ {var_name}: Not set ({description}) - Optional")
    
    return all_good

def test_github_token():
    """Test if GitHub token is valid"""
    print("\n🐙 Testing GitHub token...")
    
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ No GitHub token to test")
        return False
    
    try:
        import requests
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub token valid - User: {user_data.get('login', 'Unknown')}")
            return True
        else:
            print(f"❌ GitHub token invalid - Status: {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️ requests library not available - cannot test token")
        return True  # Don't fail if requests isn't installed
    except Exception as e:
        print(f"❌ Error testing GitHub token: {e}")
        return False

def test_aws_credentials():
    """Test AWS credentials"""
    print("\n☁️ Testing AWS credentials...")
    
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        # Try to create a session
        session = boto3.Session(
            profile_name=os.getenv('AWS_PROFILE'),
            region_name=os.getenv('AWS_REGION', 'us-west-2')
        )
        
        # Test credentials by calling STS
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS credentials valid")
        print(f"   Account: {identity.get('Account', 'Unknown')}")
        print(f"   User/Role: {identity.get('Arn', 'Unknown')}")
        
        # Test Bedrock access
        bedrock = session.client('bedrock', region_name=os.getenv('AWS_REGION', 'us-west-2'))
        models = bedrock.list_foundation_models()
        print(f"✅ Bedrock access confirmed - {len(models.get('modelSummaries', []))} models available")
        
        return True
        
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        print("   Configure with: aws configure")
        print("   Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UnauthorizedOperation':
            print("❌ AWS credentials don't have required permissions")
        else:
            print(f"❌ AWS error: {error_code}")
        return False
    except Exception as e:
        print(f"❌ Error testing AWS credentials: {e}")
        return False

def main():
    """Main environment check"""
    print("🔍 OpenFlux Environment Checker")
    print("=" * 50)
    
    checks = [
        ("Environment File", check_env_file),
        ("Environment Variables", load_and_check_env),
        ("GitHub Token", test_github_token),
        ("AWS Credentials", test_aws_credentials)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name} PASSED")
            else:
                print(f"❌ {check_name} FAILED")
        except Exception as e:
            print(f"❌ {check_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Environment Check Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Environment is properly configured!")
        print("\nYou can now run OpenFlux:")
        print("  streamlit run app.py")
    else:
        print("⚠️ Environment issues found. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Copy .env.example to .env and edit with your values")
        print("  - Get a GitHub token: https://github.com/settings/tokens")
        print("  - Configure AWS: aws configure")
        print("  - Install missing packages: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)