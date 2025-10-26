#!/bin/bash

# Quick start script for Cal.com Chatbot Frontend (Streamlit)

echo "🚀 Starting Cal.com Chatbot Frontend (Streamlit)"
echo "="

# Check if in project root
if [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root"
    exit 1
fi

# Check if backend is running
echo ""
echo "🔍 Checking backend..."
if curl -s http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8001"
else
    echo "⚠️  Backend is not running!"
    echo ""
    echo "Please start the backend first:"
    echo "  python -m calcom_chatbot.main"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if frontend venv exists
echo ""
echo "📦 Checking frontend environment..."
cd frontend

if [ ! -d "frontend_venv" ]; then
    echo "⚠️  Frontend virtual environment not found"
    echo ""
    echo "Creating frontend virtual environment..."
    python -m venv frontend_venv
    source frontend_venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "✅ Frontend environment found"
    source frontend_venv/bin/activate
fi

# Start Streamlit
echo ""
echo "="
echo "🎉 Starting Streamlit..."
echo "="
echo ""
echo "Frontend will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop"
echo ""

streamlit run streamlit_app.py

