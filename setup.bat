@echo off
REM YatriGuard Setup Script for Windows

echo 🚀 Setting up YatriGuard AI Safety System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Setup Backend
echo 📦 Setting up AI/ML Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install backend dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo ✅ Backend setup complete

REM Setup Frontend
echo 📦 Setting up Frontend...
cd ..\YatriGuard-main

REM Install frontend dependencies
echo Installing Node.js dependencies...
npm install

echo ✅ Frontend setup complete

REM Go back to root directory
cd ..

echo.
echo 🎉 Setup complete!
echo.
echo To start the system:
echo.
echo 1. Start the AI backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python start.py
echo.
echo 2. In another terminal, start the frontend:
echo    cd YatriGuard-main
echo    npm run dev
echo.
echo 3. Test the AI features:
echo    cd backend
echo    python demo_client.py
echo.
echo 🌐 Frontend: http://localhost:5173
echo 🤖 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs

pause
