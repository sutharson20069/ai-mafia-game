from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio
import os
from game_logic import MafiaGame
from ai_clients import call_ai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game state
active_games = {}

def get_speed_delay():
    """Get delay based on game speed setting"""
    speed = float(os.getenv("GAME_SPEED", "1.0"))
    base_delay = 1.0
    return max(0.5, base_delay / speed)  # Minimum 0.5 seconds

async def send_with_delay(ws, message, delay=None):
    """Send message with configurable delay"""
    if delay is None:
        delay = get_speed_delay()
    await ws.send_text(message)
    await asyncio.sleep(delay)

# 🔌 WebSocket Game Endpoint
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    game_id = id(ws)
    active_games[game_id] = {"ws": ws, "game": MafiaGame()}
    
    print(f"[CONNECT] WebSocket connected (Game ID: {game_id})")
    
    try:
        # Send initial connection message
        await send_with_delay(ws, "[CONNECT] Connected to AI Mafia Game")
        await send_with_delay(ws, "[START] Game starting...")
        
        # Main game loop
        while True:
            game = active_games[game_id]["game"]
            
            # Night phase
            suspect = await game.night(lambda msg: send_with_delay(ws, msg))
            
            # Check win condition
            if game.mafia_wins():
                await send_with_delay(ws, "[END] MAFIA WINS — GAME OVER")
                break
            
            if game.civilians_win():
                await send_with_delay(ws, "[END] CIVILIANS WIN — GAME OVER")
                break
            
            # Day phase
            await game.day(suspect, lambda msg: send_with_delay(ws, msg))
            
            # Check win condition
            if game.mafia_wins():
                await send_with_delay(ws, "[END] MAFIA WINS — GAME OVER")
                break
            
            if game.civilians_win():
                await send_with_delay(ws, "[END] CIVILIANS WIN — GAME OVER")
                break
            
            # Next round
            game.round += 1
            await send_with_delay(ws, f"[ROUND] Round {game.round} complete")
            
            # Safety: limit maximum rounds
            max_rounds = int(os.getenv("MAX_ROUNDS", "10"))
            if game.round > max_rounds:
                await send_with_delay(ws, f"[END] Game ended after {max_rounds} rounds")
                break
                
    except WebSocketDisconnect:
        print(f"[DISCONNECT] WebSocket disconnected (Game ID: {game_id})")
    except Exception as e:
        print(f"[ERROR] Game error: {e}")
        await ws.send_text(f"[ERROR] Game error: {str(e)}")
    finally:
        # Clean up
        if game_id in active_games:
            del active_games[game_id]

# 📁 Serve frontend LAST
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)