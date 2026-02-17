#!/usr/bin/env python3
"""
Startup script for the RLProfilePicturesREVAMP API.
This script handles environment setup and starts the server.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

def setup_environment():
    """Set up the environment for running the server."""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Create necessary directories
    directories = [
        "cache",
        "cache/epic",
        "cache/steam", 
        "cache/xbox",
        "cache/psn",
        "cache/switch",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Please create one based on env.example")
        print("📄 Sample configuration has been created as env.example")
        return False
    
    return True


def main():
    """Main entry point."""
    print("🚀 Starting RLProfilePicturesREVAMP API...")
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed. Please check your configuration.")
        sys.exit(1)
    
    # Import and run the application
    try:
        import uvicorn
        from config import settings
        
        print(f"🌐 Server will start on http://{settings.host}:{settings.port}")
        print(f"📚 API Documentation will be available at http://{settings.host}:{settings.port}/docs")
        print(f"🔧 Debug mode: {'ON' if settings.debug else 'OFF'}")
        
        # Check API key configurations
        missing_keys = []
        if not settings.steam_api_key:
            missing_keys.append("STEAM_API_KEY")
        if not settings.psn_npsso_token:
            missing_keys.append("PSN_NPSSO_TOKEN")
        
        if missing_keys:
            print(f"⚠️  Warning: Missing API keys: {', '.join(missing_keys)}")
            print("   Some features may not work properly without these keys.")
        
        # Start the server
        uvicorn.run(
            "main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="debug" if settings.debug else "info",
            access_log=True,
            workers=(1 if settings.debug else 2),
            timeout_keep_alive=5,
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
