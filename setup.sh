#!/bin/bash
# YatriGuard Setup Script

echo "🚀 Setting up YatriGuard AI Safety System..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Backend
echo "📦 Setting up AI/ML Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete"

# Setup Frontend
echo "📦 Setting up Frontend..."
cd ../YatriGuard-main

# Install frontend dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete"

# Go back to root directory
cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the system:"
echo ""
echo "1. Start the AI backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python start.py"
echo ""
echo "2. In another terminal, start the frontend:"
echo "   cd YatriGuard-main"
echo "   npm run dev"
echo ""
echo "3. Test the AI features:"
echo "   cd backend"
echo "   python demo_client.py"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🤖 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
