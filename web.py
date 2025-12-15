from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔌 WebSocket FIRST
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    print("✅ WebSocket connected")

    await ws.send_text("🔌 Connected to backend")
    await asyncio.sleep(1)

    await ws.send_text("🌙 Night begins")
    await asyncio.sleep(1)

    await ws.send_text("🧠 Mafia thinks: I will eliminate AI3 because it questioned me.")
    await asyncio.sleep(1)

    await ws.send_text("🛡 Doctor thinks: I will save AI3 because mafia may target it.")
    await asyncio.sleep(1)

    await ws.send_text("📢 Anonymous suspects AI4")
    await asyncio.sleep(1)

    await ws.send_text("☀ Day discussion starts")
    await asyncio.sleep(1)

    await ws.send_text("💬 AI1: AI4 looks suspicious.")
    await asyncio.sleep(1)

    await ws.send_text("💬 AI2: I agree with AI1.")
    await asyncio.sleep(1)

    await ws.send_text("🗳 Voting complete")
    await asyncio.sleep(1)

    await ws.send_text("❌ AI4 eliminated")
    await asyncio.sleep(1)

    await ws.send_text("🏴 MAFIA WINS — GAME OVER")

# 📁 Serve frontend LAST
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
