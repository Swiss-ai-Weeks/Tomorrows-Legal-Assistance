#!/usr/bin/env bash
# Startup script for Tomorrow's Legal Assistance API

echo "🚀 Starting Tomorrow's Legal Assistance API..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API Documentation at: http://localhost:8000/docs"
echo ""

# Navigate to backend directory and start the server
cd "$(dirname "$0")/backend"
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload