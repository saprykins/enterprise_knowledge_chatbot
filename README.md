# Chat Application with History

A modern chat application built with Django backend and React frontend, featuring conversation history and GitHub API integration.

## Features

- 💬 Real-time chat interface
- 📚 Conversation history with persistent storage
- 🎨 Modern, responsive UI
- 🔍 GitHub API integration for context-aware responses
- 🗑️ Delete conversations
- 📱 Mobile-friendly design

## Tech Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API framework
- **SQLite** - Database (can be configured for PostgreSQL)
- **GitHub API** - For LLM responses and context

### Frontend
- **React 18** - UI framework
- **Axios** - HTTP client
- **CSS3** - Styling

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- GitHub Personal Access Token

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd axa_rag
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
1. Copy the example environment file:
```bash
cp env.example .env
```

2. Edit `.env` file and add your credentials:
```env
# LLM Configuration
GITHUB_TOKEN=your_github_token_here

# Django Configuration
SECRET_KEY=your_django_secret_key_here
DEBUG=True

# Database Configuration (optional - defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3
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

#### Run Backend Server
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd frontend
npm install
```

#### Run Frontend Development Server
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Conversations
- `GET /api/conversations/` - List all conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}/` - Get conversation details
- `POST /api/conversations/{id}/` - Add message to conversation
- `DELETE /api/conversations/{id}/delete/` - Delete conversation

## GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with the following scopes:
   - `public_repo` (for public repository access)
   - `read:user` (for user information)
3. Copy the token and add it to your `.env` file

## Usage

1. Open the application in your browser at `http://localhost:3000`
2. Click "New chat" to start a conversation
3. Type your message and press Enter or click Send
4. View conversation history in the sidebar
5. Click on any conversation to continue it
6. Delete conversations using the delete button

## System Prompt

The application uses a very concise system prompt as requested: "Be very concise in your responses."

## Development

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

### Running Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

## Deployment

### Backend Deployment
1. Set `DEBUG=False` in production
2. Use a production database (PostgreSQL recommended)
3. Configure static files serving
4. Set up proper CORS settings

### Frontend Deployment
```bash
cd frontend
npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
