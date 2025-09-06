# OpenFlux - MCP Integration Platform

OpenFlux is a Streamlit-based application that integrates with Model Context Protocol (MCP) servers and AWS Bedrock to provide semantic search and AI-powered code analysis capabilities. It's designed to work similarly to Kiro's MCP integration, focusing on GitHub repository research and analysis.

## Features

- 🔄 **MCP Server Integration**: Connect to MCP servers for extended functionality
- 🔍 **Semantic Search**: Search through GitHub repositories using semantic understanding
- 🤖 **AI-Powered Analysis**: Use AWS Bedrock models (Claude 3.5 Sonnet V2, Amazon Nova Pro)
- 💬 **Chat Interface**: Kiro-like chat interface for natural interactions
- 📊 **Repository Insights**: Analyze repository structure and code patterns
- ☁️ **AWS Integration**: Role-based access to AWS Bedrock services

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   MCP Client     │    │  Bedrock Client │
│                 │◄──►│                  │    │                 │
│ - Chat Interface│    │ - Git Repo       │    │ - Claude 3.5    │
│ - Config Panel  │    │   Research       │    │ - Nova Pro      │
│ - Status Display│    │ - Semantic Search│    │ - Response Gen  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │   GitHub API     │
                    │                  │
                    │ - Repository     │
                    │   Access         │
                    │ - Code Search    │
                    └──────────────────┘
```

## Prerequisites

- Python 3.11+
- AWS Account with Bedrock access
- GitHub Token
- uv package manager (for MCP server)

⚠️ **Important**: For detailed setup instructions, see the **[Complete Setup Guide](SETUP_GUIDE.md)**

## Installation

### Local Development

1. **Clone the repository**:
```bash
git clone <repository-url>
cd openflux
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install uv for MCP server**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**:
```bash
streamlit run app.py
```

### AWS EC2 Deployment

1. **Launch EC2 instance** (Ubuntu 22.04 LTS recommended)

2. **Configure IAM role** with Bedrock permissions:
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

3. **Deploy using the script**:
```bash
chmod +x deploy.sh
./deploy.sh
```

4. **Configure environment**:
```bash
sudo nano /opt/openflux/.env
```

5. **Restart service**:
```bash
sudo systemctl restart openflux
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# AWS Configuration
AWS_PROFILE=your-profile-name
AWS_REGION=us-west-2

# GitHub Configuration  
GITHUB_TOKEN=your-github-token

# MCP Configuration
FASTMCP_LOG_LEVEL=ERROR

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### MCP Server Configuration

The application uses the following MCP server configuration:

```json
{
  "mcpServers": {
    "awslabs.git-repo-research-mcp-server": {
      "command": "uvx",
      "args": ["awslabs.git-repo-research-mcp-server@latest"],
      "env": {
        "AWS_PROFILE": "your-profile-name",
        "AWS_REGION": "us-west-2",
        "FASTMCP_LOG_LEVEL": "ERROR",
        "GITHUB_TOKEN": "your-github-token"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Usage

### Basic Workflow

1. **Start the application** and access the web interface
2. **Configure repository** in the sidebar
3. **Connect to MCP server** using the reconnect button
4. **Index repository** to enable semantic search
5. **Start chatting** with questions about your code

### Example Queries

- "Find all authentication functions in this repository"
- "Show me the main API endpoints"
- "What testing frameworks are used?"
- "Explain the database schema"
- "Find error handling patterns"

### Sample Repositories to Try

- `microsoft/vscode` - Popular code editor
- `facebook/react` - React JavaScript library  
- `tensorflow/tensorflow` - Machine learning framework
- `kubernetes/kubernetes` - Container orchestration

## API Reference

### MCP Client Methods

- `semantic_search(repository, query, max_results)` - Perform semantic search
- `index_repository(repository)` - Index repository for search
- `get_file_content(repository, file_path)` - Get specific file content
- `search_code(repository, pattern, file_type)` - Search code patterns
- `get_repository_structure(repository)` - Get repository structure

### Bedrock Client Methods

- `generate_response(prompt, context)` - Generate AI response
- `analyze_code_search_results(results, query)` - Analyze search results
- `explain_repository_structure(structure)` - Explain repo structure
- `suggest_search_queries(repo_info)` - Suggest useful queries

## Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**
   - Check GitHub token is valid
   - Verify uv is installed: `uv --version`
   - Check AWS credentials: `aws sts get-caller-identity`

2. **Bedrock Access Denied**
   - Verify IAM role has Bedrock permissions
   - Check model availability in your region
   - Ensure model access is enabled in Bedrock console

3. **Repository Indexing Failed**
   - Verify repository exists and is public
   - Check GitHub token permissions
   - Try with a smaller repository first

### Logs

- **Application logs**: `sudo journalctl -u openflux -f`
- **Nginx logs**: `sudo tail -f /var/log/nginx/error.log`
- **MCP server logs**: Check application console output

## Development

### Project Structure

```
openflux/
├── app.py                 # Main Streamlit application
├── mcp_client.py         # MCP server client
├── bedrock_client.py     # AWS Bedrock client
├── config.py             # Configuration management
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── deploy.sh            # Deployment script
├── .env.example         # Environment template
└── README.md           # This file
```

### Adding New MCP Servers

To extend OpenFlux to support additional MCP servers:

1. Update `config.py` with new server configuration
2. Modify `mcp_client.py` to handle new server methods
3. Add UI controls in `app.py` for server selection
4. Update the sidebar to show multiple server statuses

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review application logs
- Open an issue on GitHub

## Roadmap

- [ ] Support for multiple MCP servers
- [ ] Enhanced code visualization
- [ ] Repository comparison features
- [ ] Custom search filters
- [ ] Export functionality
- [ ] Team collaboration features