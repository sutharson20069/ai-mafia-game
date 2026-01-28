# 🧠 AI Mafia Game (NOW WORKING! 🎮)

An experimental **AI-driven Mafia (Werewolf) game** where multiple AI agents play against each other with reasoning, discussion, and deception — all observable in real time via a web interface.

This project explores **multi-agent AI interaction**, **game theory**, and **real-time orchestration** using modern web technologies.

> ✅ **Status:** Now fully working with simulated AI!
> The game runs with intelligent fallback logic that doesn't require external API keys.

---

## ✨ Features (Current & Working)

### ✅ Fully Implemented and Working
- **FastAPI backend** with WebSocket support
- **Real-time event streaming** (AI thinking → actions)
- **Modular game logic** (Mafia, Doctor, Sheriff, Civilians)
- **Web UI** to observe live AI reasoning
- **Secure environment variable** handling (`.env` ignored)
- **Multi-round game flow** with win conditions
- **Intelligent AI simulation** - works without external APIs
- **Fallback logic** for robust gameplay
- **Configurable game speed** and settings

### 🚧 Available for Enhancement
- **Real AI model integration** (OpenAI, Gemini, Groq, Mistral) - just add API keys!
- **Smarter AI memory** & suspicion tracking
- **Advanced voting** and discussion logic
- **Admin controls** (view roles, pause, step rounds)
- **UI/UX improvements** and animations

### 🔮 Future Possibilities
- **Parallel AI calls** for faster rounds
- **Player personality profiles**
- **Game replay & logs**
- **Deployment to cloud** (public demo)
- **Performance benchmarking** across models

---

## 🏗️ Tech Stack

### Backend
- **Python** 3.8+
- **FastAPI** (WebSocket support)
- **Uvicorn** (ASGI server)
- **Async game orchestration**

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript** (ES6+)
- **Bootstrap 5**
- **Responsive design**

### AI / ML (Optional - Plug and Play)
- **OpenAI** (GPT models)
- **Google Gemini**
- **Groq** (Fast LLMs)
- **Mistral** (Open-source)
- **OpenRouter** / other providers

---

## 📂 Project Structure

```
ai-mafia-game/
├── web.py                  # FastAPI app & WebSocket server
├── game_logic.py           # Core Mafia game rules (FIXED!)
├── ai_clients.py           # AI provider abstraction (WORKING!)
├── run_game.py             # Main entry point
├── test_game.py            # Test script
├── frontend/               # Web UI
│   ├── index.html          # Web interface
│   ├── app.js              # Frontend logic
│   └── style.css           # Styling
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # Documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/sutharson20069/ai-mafia-game.git
cd ai-mafia-game

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Game

```bash
# Start the game server
python run_game.py

# Or run directly
python web.py
```

### Play the Game
1. Open your browser to: **http://localhost:8000**
2. Click the **▶ Start** button
3. Watch the AI agents play Mafia in real-time!
4. Observe night phases, day discussions, and voting
5. See who wins - Mafia or Civilians!

---

## 🎮 Gameplay Overview

### Roles
- **Mafia** (1 player) - Eliminates players at night
- **Doctor** (1 player) - Saves one player per night
- **Sheriff** (1 player) - Investigates and suspects players
- **Civilians** (3 players) - Discuss and vote during the day

### Game Flow
1. **Night Phase**: Mafia kills, Doctor saves, Sheriff investigates
2. **Day Phase**: All players discuss and vote to eliminate
3. **Win Conditions**:
   - Mafia wins when they outnumber civilians
   - Civilians win when all mafia are eliminated

### Example Game Session
```
[CONNECT] Connected to AI Mafia Game
[START] Game starting...
[NIGHT] Night 1 begins
[MAFIA] Mafia (AI2) thinks: I eliminate AI6 because I suspect AI6 is the sheriff
[DOCTOR] Doctor (AI3) thinks: I save AI1 because AI1 might be targeted by mafia
[SHERIFF] Sheriff (AI5) suspects AI4
[KILL] AI6 was killed by the mafia
[DAY] Day discussion starts
[CHAT] AI1: I think AI4 is suspicious because AI4 avoided answering questions
[CHAT] AI2: I think AI1 is suspicious because AI1 has been too quiet
[CHAT] AI3: I think AI4 is suspicious because AI4 avoided answering questions
[CHAT] AI4: I think AI1 is suspicious because AI1 has been too quiet
[CHAT] AI5: I think AI4 is suspicious because Something about AI4 doesn't feel right
[VOTE] Voting complete — AI4 eliminated with 3 votes
[ROUND] Round 2 complete
[END] MAFIA WINS — GAME OVER
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file by copying `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file to customize settings:

```env
# Game settings
GAME_SPEED=1.0  # Speed multiplier (1.0 = normal speed, 2.0 = faster)
DEBUG_MODE=False  # Enable debug logging
MAX_ROUNDS=10  # Maximum game rounds

# Optional: Add real AI API keys to enhance gameplay
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
```

### Available Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `GAME_SPEED` | `1.0` | Game speed multiplier |
| `DEBUG_MODE` | `False` | Enable debug logging |
| `MAX_ROUNDS` | `10` | Maximum rounds before auto-end |
| `OPENAI_API_KEY` | `` | Optional OpenAI API key |
| `GEMINI_API_KEY` | `` | Optional Google Gemini API key |
| `GROQ_API_KEY` | `` | Optional Groq API key |
| `MISTRAL_API_KEY` | `` | Optional Mistral API key |

---

## 🛠️ Development

### Running Tests

```bash
# Run the game logic test
python test_game.py

# Test should show:
# - Game initialization
# - Night phase execution
# - Day phase execution
# - Win condition checking
# - Successful completion
```

### Adding Real AI Models

The game is designed to work with real AI APIs. To enable:

1. Install required packages:
```bash
pip install openai google-generativeai mistralai
```

2. Add your API keys to `.env`
3. The game will automatically use real AI when keys are available

### Game Logic Customization

Edit `game_logic.py` to modify:
- Player roles and distribution
- Night phase behavior
- Day phase voting logic
- Win conditions

### AI Behavior Customization

Edit `ai_clients.py` to modify:
- AI decision-making logic
- Role-specific behaviors
- Reasoning patterns

---

## 🎯 Roadmap

### ✅ Completed
- [x] Basic game structure and rules
- [x] WebSocket real-time communication
- [x] Web interface for observation
- [x] Intelligent AI simulation (no API required)
- [x] Robust fallback logic
- [x] Win condition detection
- [x] Multi-round gameplay
- [x] Configuration system

### 🚧 Next Steps
- [ ] Add real AI model integration
- [ ] Implement admin controls
- [ ] Add game history/replay
- [ ] Enhance UI with animations
- [ ] Add player statistics
- [ ] Implement personality profiles
- [ ] Add game difficulty levels

### 🔮 Future Ideas
- [ ] Multiplayer support
- [ ] Human vs AI mode
- [ ] Tournament mode
- [ ] Custom role creation
- [ ] Game balancing algorithms
- [ ] Performance metrics
- [ ] Cloud deployment

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for functions
- Keep functions small and focused
- Add comments for complex logic

---

## 📋 License

This project is open-source and available for educational and experimental use.

---

## 🙏 Acknowledgments

- Thanks to all contributors and users
- Inspired by classic Mafia/Werewolf games
- Built with modern Python and web technologies
- Special thanks to the AI community for inspiration

---

## 📬 Support

For issues, questions, or suggestions, please open an issue on GitHub.

**Enjoy the game!** 🎮🧠