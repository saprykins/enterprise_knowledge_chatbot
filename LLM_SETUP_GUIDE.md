# GitHub AI LLM Setup Guide

## 🔍 **Issue Identified**

The chat application is currently using a basic keyword-based response system instead of a real LLM. Here's how to fix it with GitHub AI models:

## 🚀 **Quick Fix Steps**

### 1. **Get GitHub Token**

1. Go to [GitHub Settings](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "Chat App AI"
4. Select scopes:
   - `public_repo` (for repository access)
   - `read:user` (for user information)
5. Copy the token

### 2. **Configure Environment**

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file and add your GitHub token
nano .env
```

Add your GitHub token to the `.env` file:
```env
# LLM Configuration (GitHub AI)
GITHUB_TOKEN=your_github_token_here

# Django Configuration
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

### 3. **Test the Setup**

```bash
# Run the test script to verify everything works
python test_llm.py
```

You should see:
```
GitHub Token configured: ✅ Yes
Status: GitHub AI openai/gpt-4.1-nano (API working)
Response: [Actual AI response]
```

## 🔧 **Current Status**

### ✅ **What's Working:**
- Database setup (SQLite)
- Frontend interface
- Conversation history
- User feedback system
- GitHub API integration

### ❌ **What's Not Working:**
- **LLM Responses** - Currently using keyword matching instead of GitHub AI
- **Model Information** - Can't identify which model is being used

## 🧪 **Testing the LLM**

### **Test 1: Check Configuration**
```bash
python test_llm.py
```

### **Test 2: Test via API**
```bash
# Start the server
cd backend && python manage.py runserver

# In another terminal, test the LLM status
curl http://localhost:8000/api/llm-status/
```

### **Test 3: Test Chat Functionality**
```bash
# Create a new conversation
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What model are you and what can you do?"}' \
  http://localhost:8000/api/conversations/
```

## 🎯 **Expected Results After Setup**

### **Before (Current):**
- Responses are generic and keyword-based
- No real AI understanding
- Can't identify the model

### **After (With GitHub AI):**
- Intelligent, contextual responses
- Can explain what model it is (openai/gpt-4.1-nano)
- Can answer complex questions
- GitHub context integration

## 💰 **Cost Information**

- **GitHub AI Models**: Free for GitHub users
- **Model**: openai/gpt-4.1-nano (fast and efficient)
- **No additional costs** for using GitHub AI

## 🔒 **Security Notes**

1. **Never commit your GitHub token** to Git
2. The `.env` file is already in `.gitignore`
3. Use environment variables in production

## 🚀 **Available Models**

You can change the model in `backend/chat/services.py`:

```python
self.model = "openai/gpt-4.1-nano"  # Current model
# Other options:
# "openai/gpt-4o-mini"
# "openai/gpt-4o"
# "anthropic/claude-3-5-sonnet"
# "meta-llama/llama-3.1-8b-instruct"
```

## 📞 **Support**

If you need help:
1. Check the test script output
2. Verify your GitHub token is correct
3. Ensure you have access to GitHub AI models
4. Check the server logs for errors

## 🎉 **Next Steps**

1. Get your GitHub token
2. Add it to the `.env` file
3. Run `python test_llm.py` to verify
4. Start the application with `./start.sh`
5. Test the chat functionality

The application will then provide intelligent, contextual responses using GitHub AI models!
