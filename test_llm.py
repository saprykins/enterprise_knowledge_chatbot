#!/usr/bin/env python3
"""
Test script to check LLM functionality and configuration.
"""

import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append('backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')
django.setup()

from chat.services import LLMService

def test_llm():
    """Test the LLM service."""
    print("🔍 Testing GitHub AI LLM Service...")
    print("=" * 50)
    
    # Check environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    
    print(f"GitHub Token configured: {'✅ Yes' if github_token else '❌ No'}")
    print()
    
    # Initialize LLM service
    llm_service = LLMService()
    
    # Test model info
    print("📊 Model Information:")
    model_info = llm_service.get_model_info()
    print(f"Status: {model_info}")
    print(f"Endpoint: {llm_service.endpoint}")
    print(f"Model: {llm_service.model}")
    print()
    
    # Test response generation
    print("💬 Testing Response Generation:")
    test_messages = [
        {'role': 'user', 'content': 'Hello, what model are you?'}
    ]
    
    try:
        response = llm_service.generate_response(test_messages)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test conversation title generation
    print("📝 Testing Title Generation:")
    try:
        title = llm_service.generate_conversation_title("What is the weather like today?")
        print(f"Generated title: {title}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    print("=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_llm()
