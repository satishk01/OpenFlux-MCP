# Environment Setup Guide

## 🚨 **Critical Issue Identified**

Your indexing is failing because **environment variables are not configured**. The MCP server needs:
- GitHub token for repository access
- AWS credentials for Bedrock embeddings

## ✅ **Step-by-Step Setup**

### 1. **Create .env File**

Copy the example and fill in your values:

```bash
# Copy the example file
cp .env.example .env
```

### 2. **Configure GitHub Token**

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Create a new token with these permissions:
   - `repo` (for private repositories)
   - `public_repo` (for public repositories)
3. Copy the token and add to `.env`:

```bash
GITHUB_TOKEN=ghp_your_actual_token_here
```

### 3. **Configure AWS Credentials**

You have several options:

#### Option A: AWS Profile (Recommended)
```bash
AWS_PROFILE=default
AWS_REGION=us-west-2
```

#### Option B: Direct Credentials
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-west-2
```

### 4. **Complete .env File Example**

```bash
# AWS Configuration
AWS_PROFILE=default
AWS_REGION=us-west-2

# GitHub Configuration  
GITHUB_TOKEN=ghp_your_actual_token_here

# MCP Configuration
FASTMCP_LOG_LEVEL=ERROR

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 5. **Verify Setup**

Run the diagnostic tool again:
```bash
python diagnose_indexing_issue.py
```

## 🔧 **AWS Bedrock Setup**

### Enable Bedrock Models

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access" 
3. Enable these embedding models:
   - `amazon.titan-embed-text-v1`
   - `amazon.titan-embed-text-v2`

### Required AWS Permissions

Your AWS user/role needs these permissions:
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

## 🧪 **Test Configuration**

### Test GitHub Access
```bash
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

### Test AWS Access
```bash
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-west-2
```

## 🚀 **After Setup**

1. **Restart your application** to load new environment variables
2. **Try indexing again** - should now work
3. **Check logs** for detailed progress

## ⚠️ **Common Issues**

### GitHub Token Issues
- Token expired → Generate new token
- Wrong permissions → Ensure `repo` scope
- Private repo → Token needs access to the repository

### AWS Issues  
- No Bedrock access → Enable model access in console
- Wrong region → Bedrock not available in all regions
- Credentials → Use `aws configure` or set environment variables

### MCP Server Issues
- Not running → Restart application
- Connection failed → Check network connectivity
- Tool not found → Verify MCP server is properly initialized

## 🎯 **Expected Success Messages**

After proper setup, you should see:
```
INFO: MCP server connected successfully
INFO: Available tools: ['create_research_repository', ...]
INFO: Using indexing tool: create_research_repository
INFO: Repository indexed successfully
```

## 📞 **Need Help?**

If you're still having issues after setup:
1. Run `python diagnose_indexing_issue.py` 
2. Share the output to identify remaining issues
3. Check application logs for detailed error messages