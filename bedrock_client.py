import boto3
import json
import logging
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class BedrockClient:
    """Client for interacting with AWS Bedrock models"""
    
    def __init__(self, region: str = "us-west-2", model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"):
        self.region = region
        self.model_id = model_id
        self.client = boto3.client('bedrock-runtime', region_name=region)
        
    def generate_response(self, prompt: str, context: str = None) -> str:
        """Generate a response using the selected Bedrock model"""
        try:
            if self.model_id.startswith("anthropic.claude"):
                return self._call_claude(prompt, context)
            elif self.model_id.startswith("amazon.nova"):
                return self._call_nova(prompt, context)
            else:
                raise ValueError(f"Unsupported model: {self.model_id}")
                
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise Exception(f"Failed to generate response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
            
    def _call_claude(self, prompt: str, context: str = None) -> str:
        """Call Claude model via Bedrock"""
        system_message = """You are OpenFlux, an AI assistant that helps developers explore and understand code repositories. You have access to semantic search capabilities through MCP (Model Context Protocol) servers.

When provided with search results from a repository, analyze the code and provide helpful insights, explanations, and suggestions. Be concise but thorough in your responses.

If no context is provided, respond as a helpful coding assistant."""

        messages = []
        
        if context:
            messages.append({
                "role": "user",
                "content": f"Context from repository search:\n{context}\n\nUser question: {prompt}"
            })
        else:
            messages.append({
                "role": "user",
                "content": prompt
            })
            
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": system_message,
            "messages": messages,
            "temperature": 0.7
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    def _call_nova(self, prompt: str, context: str = None) -> str:
        """Call Amazon Nova model via Bedrock"""
        system_message = """You are OpenFlux, an AI assistant that helps developers explore and understand code repositories. You have access to semantic search capabilities through MCP (Model Context Protocol) servers.

When provided with search results from a repository, analyze the code and provide helpful insights, explanations, and suggestions. Be concise but thorough in your responses.

If no context is provided, respond as a helpful coding assistant."""

        messages = []
        
        # Add system message
        messages.append({
            "role": "user",
            "content": [{"text": system_message}]
        })
        
        if context:
            user_content = f"Context from repository search:\n{context}\n\nUser question: {prompt}"
        else:
            user_content = prompt
            
        messages.append({
            "role": "user", 
            "content": [{"text": user_content}]
        })
        
        body = {
            "messages": messages,
            "max_tokens": 4000,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']
        
    def analyze_code_search_results(self, search_results: Dict[str, Any], query: str) -> str:
        """Analyze code search results and provide insights"""
        context = f"Search Query: {query}\nSearch Results: {json.dumps(search_results, indent=2)}"
        
        analysis_prompt = f"""Analyze the following code search results and provide insights:

1. Summarize what was found
2. Explain the relevant code patterns or structures
3. Suggest how this code might be used or modified
4. Point out any interesting implementation details
5. Recommend next steps for exploration

Search Results:
{context}"""

        return self.generate_response(analysis_prompt)
        
    def explain_repository_structure(self, structure: Dict[str, Any]) -> str:
        """Explain repository structure"""
        prompt = f"""Analyze this repository structure and provide an overview:

1. What type of project this appears to be
2. Key directories and their purposes  
3. Main technologies or frameworks used
4. Architecture patterns observed
5. Entry points and important files

Repository Structure:
{json.dumps(structure, indent=2)}"""

        return self.generate_response(prompt)
        
    def suggest_search_queries(self, repository_info: str) -> List[str]:
        """Suggest useful search queries for a repository"""
        prompt = f"""Based on this repository information, suggest 5-7 useful search queries that would help a developer understand the codebase:

Repository Info:
{repository_info}

Provide queries that would reveal:
- Main functionality
- API endpoints or interfaces
- Configuration patterns
- Error handling
- Testing approaches
- Key algorithms or business logic

Return as a simple list."""

        response = self.generate_response(prompt)
        
        # Extract queries from response (simple parsing)
        lines = response.split('\n')
        queries = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line.startswith('1.')):
                # Clean up the line
                query = line.lstrip('-*0123456789. ').strip()
                if query:
                    queries.append(query)
                    
        return queries[:7]  # Limit to 7 queries