#!/bin/bash

# Start backend server
cd backend/src
source ../.venv/bin/activate
python3 manage.py migrate
python3 manage.py runserver &

# Start frontend server
cd ../../frontend
bun run dev &

echo "Both servers are running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173" 