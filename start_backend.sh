#!/usr/bin/env bash
# Startup script for Tomorrow's Legal Assistance API

echo "🚀 Starting Tomorrow's Legal Assistance API..."
echo "📍 API will be available at: http://localhost:8000"
echo "📚 API Documentation at: http://localhost:8000/docs"
echo ""

uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload