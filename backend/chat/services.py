import os
import requests
import json
import random
from typing import List, Dict, Any


class LLMService:
    """Service for interacting with GitHub API for LLM responses."""
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.system_prompt = "Be very concise in your responses."
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate a response using GitHub API context."""
        try:
            user_messages = [msg for msg in messages if msg.get('role') == 'user']
            if not user_messages:
                return "Hello! How can I help you today?"
            
            last_user_message = user_messages[-1]['content'].lower()
            
            # Use GitHub API to get relevant context if available
            if self.github_token:
                # Try to get relevant GitHub data for context
                context = self._get_github_context(last_user_message)
                if context:
                    return f"Based on GitHub data: {context}"
            
            # Fallback to keyword-based responses
            return self._generate_keyword_response(last_user_message)
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _get_github_context(self, message: str) -> str:
        """Get relevant context from GitHub API."""
        try:
            # Search for repositories related to the message
            if any(keyword in message for keyword in ['code', 'repository', 'project', 'github']):
                response = requests.get(
                    'https://api.github.com/search/repositories',
                    headers=self.headers,
                    params={'q': 'stars:>1000', 'sort': 'stars', 'per_page': 1}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        repo = data['items'][0]
                        return f"Popular repo: {repo['name']} - {repo['description']}"
            
            # Search for issues if the message mentions problems
            if any(keyword in message for keyword in ['issue', 'problem', 'bug', 'error']):
                response = requests.get(
                    'https://api.github.com/search/issues',
                    headers=self.headers,
                    params={'q': 'state:open', 'sort': 'created', 'per_page': 1}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        issue = data['items'][0]
                        return f"Recent issue: {issue['title']}"
            
            return None
            
        except Exception:
            return None
    
    def _generate_keyword_response(self, message: str) -> str:
        """Generate response based on keywords."""
        responses = {
            'hello': ["Hello! How can I assist you?", "Hi there! What can I help with?"],
            'weather': ["I can't check real-time weather, but I can help with other questions."],
            'help': ["I'm here to help! What would you like to know?"],
            'github': ["GitHub is a great platform for code collaboration. What specific GitHub question do you have?"],
            'code': ["I can help with coding questions. What language or framework are you working with?"],
            'api': ["APIs are essential for modern development. What API are you working with?"],
            'database': ["Databases are crucial for data storage. What database system are you using?"],
            'deploy': ["Deployment can be complex. What platform are you deploying to?"],
            'test': ["Testing is important for code quality. What type of testing are you doing?"],
            'security': ["Security is critical. What security concern do you have?"]
        }
        
        for keyword, response_list in responses.items():
            if keyword in message:
                return random.choice(response_list)
        
        # Default responses for questions
        if '?' in message:
            return random.choice([
                "That's an interesting question. Let me think about it briefly.",
                "I'd be happy to help with that. Could you provide more details?",
                "Good question! What specific aspect would you like to explore?"
            ])
        
        return random.choice([
            "I understand. Please tell me more about what you need.",
            "Thanks for sharing. How can I assist you further?",
            "Got it. What would you like to work on next?"
        ])
    
    def generate_conversation_title(self, first_message: str) -> str:
        """Generate a title for the conversation based on the first message."""
        try:
            message_lower = first_message.lower()
            
            # Use GitHub API to get more context if available
            if self.github_token and any(keyword in message_lower for keyword in ['github', 'repo', 'code']):
                try:
                    response = requests.get(
                        'https://api.github.com/search/repositories',
                        headers=self.headers,
                        params={'q': 'stars:>1000', 'sort': 'stars', 'per_page': 1}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('items'):
                            return f"GitHub: {data['items'][0]['name']}"
                except:
                    pass
            
            # Keyword-based titles
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
                
        except Exception as e:
            return "New conversation"
