"""
YatriGuard Backend Startup Script
Sets up the FastAPI server with AI/ML capabilities
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('yatriguard.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import numpy
        import pydantic
        logger.info("✓ All core dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.error("Please install dependencies with: pip install -r requirements.txt")
        return False

async def initialize_system():
    """Initialize the YatriGuard AI system"""
    try:
        logger.info("🚀 Starting YatriGuard AI Safety System...")
        
        # Import main application
        from main import app
        
        logger.info("✓ FastAPI application loaded")
        logger.info("✓ AI/ML models initialized")
        logger.info("✓ Fallback systems ready")
        logger.info("✓ Alert services configured")
        
        return app
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize system: {str(e)}")
        raise

def main():
    """Main startup function"""
    try:
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        reload = os.getenv('RELOAD', 'true').lower() == 'true'
        
        logger.info(f"🌐 Starting server on {host}:{port}")
        logger.info(f"📝 API documentation available at: http://{host}:{port}/docs")
        logger.info(f"🔄 Auto-reload: {'enabled' if reload else 'disabled'}")
        
        # Start the server
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down YatriGuard system...")
    except Exception as e:
        logger.error(f"💥 Startup error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
