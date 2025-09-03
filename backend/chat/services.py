import os
import requests
import json
from typing import List, Dict, Any


class LLMService:
    """Service for interacting with GitHub AI models."""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        
        # GitHub AI Configuration
        self.endpoint = "https://models.github.ai/inference"
        self.model = "openai/gpt-4.1-nano"  # You can change this model
        
        self.headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'chat-app'
        } if self.github_token else {}
        
        self.github_api_headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        } if self.github_token else {}
        
        self.system_prompt = "You are a helpful AI assistant. Be very concise in your responses."
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using GitHub AI models."""
        try:
            if not self.github_token:
                return "Error: GitHub token not configured. Please set GITHUB_TOKEN in your environment."
            
            # Add system message at the beginning if not present
            if not messages or messages[0].get('role') != 'system':
                messages.insert(0, {'role': 'system', 'content': self.system_prompt})
            
            # No GitHub context needed - removed for simplicity
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 1,
                "top_p": 1,
                "max_tokens": 200
            }
            
            response = requests.post(
                f"{self.endpoint}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                return f"Error: API returned status {response.status_code}: {response.text}"
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _get_github_context(self, message: str) -> str:
        """Get relevant context from GitHub API."""
        try:
            context_parts = []
            
            # Search for repositories related to the message
            if any(keyword in message.lower() for keyword in ['code', 'repository', 'project', 'github', 'repo']):
                response = requests.get(
                    'https://api.github.com/search/repositories',
                    headers=self.github_api_headers,
                    params={'q': 'stars:>1000', 'sort': 'stars', 'per_page': 3}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        repos = data['items'][:3]
                        repo_info = []
                        for repo in repos:
                            repo_info.append(f"{repo['name']}: {repo['description']}")
                        context_parts.append(f"Popular repositories: {'; '.join(repo_info)}")
            
            # Search for issues if the message mentions problems
            if any(keyword in message.lower() for keyword in ['issue', 'problem', 'bug', 'error', 'fix']):
                response = requests.get(
                    'https://api.github.com/search/issues',
                    headers=self.github_api_headers,
                    params={'q': 'state:open', 'sort': 'created', 'per_page': 3}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        issues = data['items'][:3]
                        issue_info = []
                        for issue in issues:
                            issue_info.append(f"{issue['title']}")
                        context_parts.append(f"Recent issues: {'; '.join(issue_info)}")
            
            return ' '.join(context_parts) if context_parts else None
            
        except Exception:
            return None
    
    def generate_conversation_title(self, first_message: str) -> str:
        """Generate a title for the conversation using GitHub AI."""
        try:
            if not self.github_token:
                return self._generate_simple_title(first_message)
            
            payload = {
                "model": self.model,
                "messages": [
                    {'role': 'system', 'content': 'Generate a very short title (max 5 words) for this conversation.'},
                    {'role': 'user', 'content': first_message}
                ],
                "temperature": 1,
                "top_p": 1,
                "max_tokens": 20
            }
            
            response = requests.post(
                f"{self.endpoint}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                return self._generate_simple_title(first_message)
            
        except Exception as e:
            return self._generate_simple_title(first_message)
    
    def _generate_simple_title(self, first_message: str) -> str:
        """Fallback title generation based on keywords."""
        message_lower = first_message.lower()
        
        if 'weather' in message_lower:
            return "Weather inquiry"
        elif 'help' in message_lower:
            return "Help request"
        elif 'migration' in message_lower or 'oracle' in message_lower:
            return "Migration to Oracle"
        elif 'latency' in message_lower or 'performance' in message_lower:
            return "Latency issue"
        elif 'github' in message_lower:
            return "GitHub discussion"
        elif 'code' in message_lower or 'programming' in message_lower:
            return "Code discussion"
        elif '?' in first_message:
            return "Question"
        else:
            return "New conversation"
    
    def get_model_info(self) -> str:
        """Get information about the current model being used."""
        if not self.github_token:
            return "No GitHub token configured"
        
        try:
            # Test the API connection
            payload = {
                "model": self.model,
                "messages": [{'role': 'user', 'content': 'Hello'}],
                "temperature": 1,
                "top_p": 1,
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.endpoint}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return f"GitHub AI {self.model} (API working)"
            else:
                return f"GitHub AI API Error: Status {response.status_code}"
                
        except Exception as e:
            return f"GitHub AI API Error: {str(e)}"
