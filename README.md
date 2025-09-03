# Chat Application with RAG (Retrieval-Augmented Generation)

A modern chat application built with Django backend and React frontend, featuring conversation history, GitHub AI integration, and **RAG (Retrieval-Augmented Generation)** for company knowledge management.

## 🚀 Features

- 💬 **Real-time chat interface** with conversation history
- 📚 **RAG System** - Upload and query company documents
- 🎨 **Modern, responsive UI** with admin interface
- 🔍 **GitHub AI integration** for context-aware responses
- 🎛️ **3-Position Data Switcher** - Use company data, Both (intelligent), or LLM only
- 🗑️ **Delete conversations** and manage data sources
- 📱 **Mobile-friendly design**
- 🔄 **Async document processing** with Celery
- 📊 **Analytics and feedback** system

## 🎛️ Data Source Control

The application features a **3-Position Switcher** that controls how the AI responds to user queries:

### **Use** 📄
- Only uses company data from the RAG system
- Best for company-specific questions
- Fastest response time

### **Both** 🤖📄
- **Intelligent RAG + LLM combination**
- First checks if the question relates to company data
- If RAG-relevant: Rephrases question, asks for confirmation, then answers using company data + general knowledge
- If not RAG-relevant: Uses LLM knowledge only
- Provides the most comprehensive and accurate responses

### **Not Use** 🤖
- Only uses the LLM's general knowledge
- Best for general questions not related to company data
- No company information included

## 🏗️ Architecture

### Backend (Django + LangChain)
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API framework
- **LangChain** - RAG orchestration
- **ChromaDB** - Vector database
- **Celery + Redis** - Async task processing
- **SQLite** - Relational database

### Frontend (React)
- **React 18** - UI framework
- **Axios** - HTTP client
- **CSS3** - Modern styling

## 📋 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis (for Celery)
- GitHub Personal Access Token

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd enterprise_knowledge_chatbot
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Environment Configuration
1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` file and add your credentials:
```env
# LLM Configuration (GitHub AI)
GITHUB_TOKEN=your_github_token_here

# Django Configuration
SECRET_KEY=your_django_secret_key_here
DEBUG=True

# Database Configuration (optional - defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Celery Configuration (for async document processing)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

#### Database Setup
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

### 4. Start All Services

#### Option 1: Use the start script
```bash
chmod +x start.sh
./start.sh
```

#### Option 2: Start manually
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
cd backend
celery -A chat_app worker --loglevel=info

# Terminal 3: Start Django backend
cd backend
python manage.py runserver

# Terminal 4: Start React frontend
cd frontend
npm start
```

## 🎯 Usage

### Chat Interface
1. Open the application at `http://localhost:3000`
2. Toggle "Use company data" to enable RAG
3. Start a conversation - the AI will use company documents when available
4. View conversation history in the sidebar

### Admin Interface
1. Click "Admin" button in the sidebar
2. **Upload Documents**: Drag & drop PDF files
3. **Manage Data Sources**: Toggle active/inactive sources
4. **View Statistics**: Monitor RAG system performance
5. **Delete Sources**: Remove documents from the knowledge base

## 🔧 API Endpoints

### Conversations
- `GET /api/conversations/` - List all conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}/` - Get conversation details
- `POST /api/conversations/{id}/` - Add message to conversation
- `DELETE /api/conversations/{id}/delete/` - Delete conversation

### RAG System
- `GET /api/data-sources/` - List all data sources
- `POST /api/data-sources/` - Upload new document
- `PUT /api/data-sources/{id}/` - Update data source (toggle active)
- `DELETE /api/data-sources/{id}/` - Delete data source
- `GET /api/rag-stats/` - Get RAG system statistics
- `GET /api/conversations/{id}/rag-queries/` - Get RAG query history

### Feedback
- `POST /api/conversations/{id}/feedback/` - Submit user feedback
- `GET /api/conversations/{id}/feedback/list/` - Get conversation feedback

## 🧠 RAG System Details

### How it Works
1. **Document Upload**: PDF files are uploaded via the admin interface
2. **Async Processing**: Celery processes documents in the background
3. **Chunking**: Documents are split into manageable chunks
4. **Embedding**: Chunks are converted to vector embeddings using sentence-transformers
5. **Storage**: Embeddings are stored in ChromaDB vector database
6. **Retrieval**: When querying, relevant chunks are retrieved based on similarity
7. **Generation**: LLM generates responses using retrieved context

### Supported Document Types
- ✅ **PDF** (currently supported)
- 🔄 **Confluence** (planned)
- 🔄 **Jira** (planned)
- 🔄 **SharePoint** (planned)

### Vector Database
- **ChromaDB** - Persistent vector database
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Chunk Size**: 1000 characters with 200 character overlap

## 🔑 GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with the following scopes:
   - `public_repo` (for public repository access)
   - `read:user` (for user information)
3. Copy the token and add it to your `.env` file

## 🛠️ Development

### Backend Development
```bash
cd backend
python manage.py runserver
```

### Frontend Development
```bash
cd frontend
npm start
```

### Celery Worker
```bash
cd backend
celery -A chat_app worker --loglevel=info
```

### Running Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

## 📊 Monitoring

### RAG Statistics
- Total data sources
- Active sources
- Total document chunks
- Total tokens processed
- Processing status

### Performance Metrics
- Retrieval time
- Generation time
- Token usage
- Query history

## 🚀 Deployment

### Backend Deployment
1. Set `DEBUG=False` in production
2. Use a production database (PostgreSQL recommended)
3. Configure static files serving
4. Set up proper CORS settings
5. Configure Redis for Celery
6. Set up proper logging

### Frontend Deployment
```bash
cd frontend
npm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🔮 Future Enhancements

- [ ] Confluence integration
- [ ] Jira integration  
- [ ] SharePoint integration
- [ ] Advanced document preprocessing
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] User authentication and permissions
- [ ] API rate limiting
- [ ] Document versioning
