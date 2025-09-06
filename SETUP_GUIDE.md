# OpenFlux Setup Guide

This guide will help you set up OpenFlux with all required dependencies and configurations.

## Prerequisites

### 1. Install Python Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Install uv/uvx (Required for MCP Server)

The MCP server requires `uvx` to run. Install it using one of these methods:

**Option A: Using pip**
```bash
pip install uv
```

**Option B: Using the official installer**
```bash
# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Option C: Using package managers**
```bash
# On macOS with Homebrew
brew install uv

# On Windows with Chocolatey
choco install uv

# On Windows with Scoop
scoop install uv
```

After installation, verify it works:
```bash
uvx --version
```

### 3. Set Up GitHub Token

You need a GitHub Personal Access Token to access repositories:

1. **Create a token**: 
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Give it a descriptive name like "OpenFlux MCP Access"

2. **Set permissions**:
   - For **public repositories**: Select `public_repo` scope
   - For **private repositories**: Select `repo` scope
   - Optionally add `read:org` if you need organization access

3. **Copy the token** and save it securely

### 4. Configure Environment Variables

Create a `.env` file in the project root with your configuration:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file with your values:

```env
# AWS Configuration (for EC2 instances, you might not need these)
AWS_REGION=us-west-2
AWS_PROFILE=default

# GitHub Configuration (REQUIRED)
GITHUB_TOKEN=your_actual_github_token_here

# MCP Configuration
FASTMCP_LOG_LEVEL=ERROR

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

**Important**: Replace `your_actual_github_token_here` with the token you created in step 3.

## AWS Configuration

### For EC2 Instances

If running on EC2, ensure your instance has an IAM role with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### For Local Development

If running locally, you can use AWS credentials in your `.env` file:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
```

## Testing Your Setup

### 1. Test MCP Connection

Run the MCP connection test:

```bash
python test_mcp_simple.py
```

This will check:
- ✅ uvx is available
- ✅ GitHub token is set
- ✅ MCP server can start

### 2. Test AWS/Bedrock Connection

Run the Bedrock test:

```bash
python test_bedrock.py
```

This will check:
- ✅ AWS credentials are working
- ✅ Bedrock access is available
- ✅ Models can be invoked

### 3. Run the Application

If all tests pass, start the application:

```bash
streamlit run app.py
```

The app should be available at: http://localhost:8501

## Troubleshooting

### Common Issues

**1. "uvx command not found"**
- Solution: Install uv using the instructions above
- Verify: Run `uvx --version`

**2. "GITHUB_TOKEN not set"**
- Solution: Add your GitHub token to the `.env` file
- Verify: Check the token works at https://github.com/settings/tokens

**3. "MCP server process failed to start"**
- Check your GitHub token is valid
- Ensure uvx can access the internet to download the MCP server
- Try running manually: `uvx awslabs.git-repo-research-mcp-server@latest`

**4. "Bedrock API error"**
- Check your AWS credentials are correct
- Ensure you have Bedrock permissions
- Verify the region supports the models you're trying to use

**5. "ValidationException" with models**
- This usually means incorrect parameters for the model
- Try switching between Claude and Nova models
- Check the logs for specific parameter errors

### Getting Help

1. **Check the logs**: Look at the console output when running the app
2. **Run diagnostics**: Use the "AWS Diagnostics" button in the app sidebar
3. **Test components**: Run the individual test scripts to isolate issues
4. **Environment**: Use "Reload Env" button after changing `.env` file

## Usage

Once everything is set up:

1. **Connect to MCP**: Click "Reconnect" in the sidebar
2. **Select a model**: Choose between Claude 3.5 Sonnet V2 (uses inference profile: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`) or Amazon Nova Pro
3. **Set repository**: Enter a GitHub repository (e.g., `microsoft/vscode`)
4. **Index repository**: Click "Index Repository" to prepare it for search
5. **Start chatting**: Ask questions about the code or search for specific functionality

Example queries:
- "Search for authentication functions"
- "Find error handling patterns"
- "Show me the main entry point"
- "Look for API endpoints"

Enjoy exploring code with OpenFlux! 🚀