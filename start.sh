#!/bin/bash

# Start Redis (if not already running)
echo "Starting Redis..."
redis-server --daemonize yes 2>/dev/null || echo "Redis already running or not available"

# Start Celery worker
echo "Starting Celery worker..."
cd backend
source ../venv/bin/activate
celery -A chat_app worker --loglevel=info &
CELERY_PID=$!

# Start Django backend
echo "Starting Django backend..."
source ../venv/bin/activate
python manage.py runserver &
DJANGO_PID=$!

# Start React frontend
echo "Starting React frontend..."
cd ../frontend
DANGEROUSLY_DISABLE_HOST_CHECK=true npm start &
REACT_PID=$!

# Wait for all processes
echo ""
echo "🚀 All services started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000/api/"
echo "📊 Admin: http://localhost:8000/admin/"
echo ""
echo "Press Ctrl+C to stop all services."
trap "echo 'Stopping services...'; kill $CELERY_PID $DJANGO_PID $REACT_PID; exit" INT
wait
