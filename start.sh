#!/bin/bash

# Start the Django backend server
echo "Starting Django backend server..."
cd backend
python manage.py runserver &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the React frontend server
echo "Starting React frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Both servers are starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop the servers
wait $BACKEND_PID $FRONTEND_PID

# Cleanup on exit
echo "Stopping servers..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
