#!/bin/bash

# Start Redis (if not already running)
echo "Starting Redis..."
redis-server --daemonize yes 2>/dev/null || echo "Redis already running or not available"

# Start Celery worker
echo "Starting Celery worker..."
cd backend
celery -A chat_app worker --loglevel=info &
CELERY_PID=$!

# Start Django backend
echo "Starting Django backend..."
python manage.py runserver &
DJANGO_PID=$!

# Start React frontend
echo "Starting React frontend..."
cd ../frontend
npm start &
REACT_PID=$!

# Wait for all processes
echo "All services started. Press Ctrl+C to stop all services."
trap "echo 'Stopping services...'; kill $CELERY_PID $DJANGO_PID $REACT_PID; exit" INT
wait
