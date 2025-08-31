# LLM Setup Guide

## 🔍 **Issue Identified**

The chat application is currently using a basic keyword-based response system instead of a real LLM. Here's how to fix it:

## 🚀 **Quick Fix Steps**

### 1. **Get OpenAI API Key**

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to "API Keys" section
4. Create a new API key
5. Copy the key (it starts with `sk-`)

### 2. **Configure Environment**

```bash
# Copy the example environment file
cp env.example .env

# Edit the .env file and add your OpenAI API key
nano .env
```

Add your OpenAI API key to the `.env` file:
```env
# LLM Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here
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
OpenAI API Key configured: ✅ Yes
Status: OpenAI GPT-3.5-turbo (API working)
Response: [Actual GPT response]
```

## 🔧 **Current Status**

### ✅ **What's Working:**
- Database setup (SQLite)
- Frontend interface
- Conversation history
- User feedback system
- GitHub API integration

### ❌ **What's Not Working:**
- **LLM Responses** - Currently using keyword matching instead of GPT
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

### **After (With OpenAI):**
- Intelligent, contextual responses
- Can explain what model it is (GPT-3.5-turbo)
- Can answer complex questions
- GitHub context integration

## 💰 **Cost Information**

- **OpenAI GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Typical chat response**: ~100-200 tokens
- **Estimated cost per conversation**: ~$0.0004-0.0008

## 🔒 **Security Notes**

1. **Never commit your API key** to Git
2. The `.env` file is already in `.gitignore`
3. Use environment variables in production

## 🚀 **Alternative LLM Options**

If you don't want to use OpenAI, you can modify `backend/chat/services.py` to use:

1. **Local Models** (Ollama, LM Studio)
2. **Other APIs** (Anthropic Claude, Google Gemini)
3. **Open Source Models** (Llama, Mistral)

## 📞 **Support**

If you need help:
1. Check the test script output
2. Verify your API key is correct
3. Ensure you have sufficient OpenAI credits
4. Check the server logs for errors

## 🎉 **Next Steps**

1. Get your OpenAI API key
2. Add it to the `.env` file
3. Run `python test_llm.py` to verify
4. Start the application with `./start.sh`
5. Test the chat functionality

The application will then provide intelligent, contextual responses using GPT-3.5-turbo!
