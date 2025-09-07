#!/usr/bin/env python3
"""
Interactive script to set up .env file
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with user input"""
    
    print("🔧 Environment Setup Wizard")
    print("=" * 50)
    
    env_file = Path(".env")
    
    if env_file.exists():
        print(f"⚠️  .env file already exists")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Cancelled.")
            return False
    
    print("\n📋 Please provide the following information:")
    print("(Press Enter to skip optional fields)")
    
    # GitHub Token
    print("\n1. **GitHub Token** (Required)")
    print("   Go to: GitHub → Settings → Developer settings → Personal access tokens")
    print("   Permissions needed: 'repo' for private repos, 'public_repo' for public repos")
    github_token = input("   GitHub Token: ").strip()
    
    if not github_token:
        print("❌ GitHub token is required for repository access")
        return False
    
    # AWS Configuration
    print("\n2. **AWS Configuration** (Required)")
    print("   Choose option:")
    print("   A) Use AWS Profile (recommended)")
    print("   B) Use direct credentials")
    
    aws_option = input("   Choose (A/B): ").upper().strip()
    
    aws_profile = ""
    aws_access_key = ""
    aws_secret_key = ""
    
    if aws_option == 'A':
        aws_profile = input("   AWS Profile name (default): ").strip() or "default"
    elif aws_option == 'B':
        aws_access_key = input("   AWS Access Key ID: ").strip()
        aws_secret_key = input("   AWS Secret Access Key: ").strip()
        
        if not aws_access_key or not aws_secret_key:
            print("❌ Both AWS Access Key ID and Secret Access Key are required")
            return False
    else:
        print("❌ Invalid option selected")
        return False
    
    # AWS Region
    aws_region = input("   AWS Region (us-west-2): ").strip() or "us-west-2"
    
    # Optional settings
    print("\n3. **Optional Settings**")
    log_level = input("   MCP Log Level (ERROR): ").strip() or "ERROR"
    port = input("   Streamlit Port (8501): ").strip() or "8501"
    address = input("   Streamlit Address (0.0.0.0): ").strip() or "0.0.0.0"
    
    # Create .env content
    env_content = f"""# AWS Configuration
"""
    
    if aws_profile:
        env_content += f"AWS_PROFILE={aws_profile}\n"
    
    if aws_access_key and aws_secret_key:
        env_content += f"AWS_ACCESS_KEY_ID={aws_access_key}\n"
        env_content += f"AWS_SECRET_ACCESS_KEY={aws_secret_key}\n"
    
    env_content += f"""AWS_REGION={aws_region}

# GitHub Configuration
GITHUB_TOKEN={github_token}

# MCP Configuration
FASTMCP_LOG_LEVEL={log_level}

# Streamlit Configuration
STREAMLIT_SERVER_PORT={port}
STREAMLIT_SERVER_ADDRESS={address}
"""
    
    # Write .env file
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"📁 Location: {env_file.absolute()}")
        
        # Show masked content
        print(f"\n📋 Configuration:")
        lines = env_content.strip().split('\n')
        for line in lines:
            if line.startswith('#') or not line.strip():
                print(f"   {line}")
            elif '=' in line:
                key, value = line.split('=', 1)
                if 'TOKEN' in key or 'KEY' in key:
                    masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                    print(f"   {key}={masked}")
                else:
                    print(f"   {key}={value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def verify_setup():
    """Verify the setup by checking environment variables"""
    
    print("\n🧪 Verifying Setup...")
    
    # Load .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        return False
    
    # Check required variables
    required_vars = ['GITHUB_TOKEN', 'AWS_REGION']
    aws_cred_vars = ['AWS_PROFILE', 'AWS_ACCESS_KEY_ID']
    
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    # Check AWS credentials (either profile or keys)
    has_profile = bool(os.getenv('AWS_PROFILE'))
    has_keys = bool(os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))
    
    if not has_profile and not has_keys:
        missing.append('AWS_CREDENTIALS')
    
    if missing:
        print(f"❌ Missing variables: {missing}")
        return False
    else:
        print("✅ All required variables are set")
        return True

def show_next_steps():
    """Show next steps after setup"""
    
    print("\n🚀 Next Steps:")
    print("=" * 30)
    
    print("\n1. **Restart your application** to load new environment variables")
    print("2. **Test the setup:**")
    print("   python diagnose_indexing_issue.py")
    print("\n3. **Try indexing a repository:**")
    print("   Use your application's indexing feature")
    print("\n4. **Check for success messages:**")
    print("   INFO: MCP server connected successfully")
    print("   INFO: Repository indexed successfully")
    
    print("\n💡 **Troubleshooting:**")
    print("   • If GitHub access fails → Check token permissions")
    print("   • If AWS access fails → Verify credentials and Bedrock access")
    print("   • If MCP fails → Restart application and check logs")

def main():
    """Main setup function"""
    
    print("Welcome to the MCP Environment Setup Wizard!")
    print("This will help you configure the required environment variables.")
    
    if create_env_file():
        if verify_setup():
            show_next_steps()
            print("\n🎉 Setup completed successfully!")
            return True
        else:
            print("\n❌ Setup verification failed")
            return False
    else:
        print("\n❌ Setup failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)