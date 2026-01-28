#!/usr/bin/env python3

"""
AI Mafia Game - Main Entry Point
Run this script to start the game server
"""

import uvicorn
from web import app

if __name__ == "__main__":
    print("Starting AI Mafia Game Server...")
    print("Open your browser to: http://localhost:8000")
    print("WebSocket will connect automatically")
    print("Enjoy the AI-powered Mafia game!")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)