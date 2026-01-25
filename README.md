# 🧠 AI Mafia Game (WORK IS NO LONGER SUPPORTED 🚧)

An experimental **AI-driven Mafia (Werewolf) game** where multiple AI agents play against each other with reasoning, discussion, and deception — all observable in real time via a web interface.

This project explores **multi-agent AI interaction**, **game theory**, and **real-time orchestration** using modern web technologies.

> ⚠️ **Status:** Actively not under development.  
> Features, architecture, and gameplay mechanics are not evolving.

---

## ✨ Features (Current & Planned)

### ✅ Implemented
- FastAPI backend with WebSocket support
- Real-time event streaming (AI thinking → actions)
- Modular game logic (Mafia, Doctor, Sheriff, Civilians)
- Web UI to observe live AI reasoning
- Secure environment variable handling (`.env` ignored)
- Multi-round game flow (prototype)

### 🚧 In Progress
- Real AI model integration (OpenAI, Gemini, Groq, Mistral)
- Smarter AI memory & suspicion tracking
- Advanced voting and discussion logic
- Admin controls (view roles, pause, step rounds)
- UI/UX improvements and animations

### 🔮 Planned
- Parallel AI calls for faster rounds
- Player personality profiles
- Game replay & logs
- Deployment to cloud (public demo)
- Performance benchmarking across models

---

## 🏗️ Tech Stack

### Backend
- **Python**
- **FastAPI**
- **WebSockets (uvicorn)**
- Async game orchestration

### Frontend
- **HTML**
- **CSS**
- **JavaScript**
- **Bootstrap**
- Responsive design

### AI / ML (Planned & Optional)
- OpenAI
- Gemini
- Groq
- Mistral
- OpenRouter / other providers

---

## 📂 Project Structure

ai-mafia-game/
├── web.py # FastAPI app & WebSocket server
├── game_logic.py # Core Mafia game rules
├── ai_clients.py # AI provider abstraction
├── frontend/
│ ├── index.html # Web UI
│ ├── app.js # Frontend logic & WebSocket client
│ └── style.css # Styling
├── .gitignore
└── .env.example # Environment variable template
