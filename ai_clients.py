"""
Enhanced AI Clients for AI Mafia Game
Supports both real AI APIs and intelligent fallback simulation
"""

import os
import random
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check which AI providers are available
HAS_OPENAI = os.getenv("OPENAI_API_KEY") is not None
HAS_GEMINI = os.getenv("GEMINI_API_KEY") is not None
HAS_GROQ = os.getenv("GROQ_API_KEY") is not None
HAS_MISTRAL = os.getenv("MISTRAL_API_KEY") is not None

# Import real AI clients if available
real_ai_available = False

try:
    if HAS_OPENAI:
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        real_ai_available = True
    else:
        openai_client = None
except ImportError:
    openai_client = None
    HAS_OPENAI = False

try:
    if HAS_GEMINI:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        real_ai_available = True
    else:
        genai = None
except ImportError:
    genai = None
    HAS_GEMINI = False

try:
    if HAS_GROQ:
        from openai import AsyncOpenAI
        groq_client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        real_ai_available = True
    else:
        groq_client = None
except ImportError:
    groq_client = None
    HAS_GROQ = False

try:
    if HAS_MISTRAL:
        from mistralai.async_client import MistralAsyncClient
        mistral_client = MistralAsyncClient(api_key=os.getenv("MISTRAL_API_KEY"))
        real_ai_available = True
    else:
        mistral_client = None
except ImportError:
    mistral_client = None
    HAS_MISTRAL = False

# ---------------------------------------
# SYSTEM PROMPT (VERY IMPORTANT)
# ---------------------------------------
SYSTEM_PROMPT = """
You are playing the game Mafia.

Rules:
- Choose ONLY from alive players
- Respond ONLY in valid JSON
- JSON format:
{
  "target": "AIx",
  "reason": "your reasoning"
}
Do not add extra text.
"""

# Memory system for AI agents
class AIMemory:
    def __init__(self):
        self.suspicion_levels = {}
        self.conversation_history = []
        self.actions_taken = []
        self.roles_revealed = set()
        
    def update_suspicion(self, player, amount):
        """Update suspicion level for a player"""
        self.suspicion_levels[player] = self.suspicion_levels.get(player, 0) + amount
        
    def add_conversation(self, speaker, message):
        """Add conversation to memory"""
        self.conversation_history.append({"speaker": speaker, "message": message})\n        if len(self.conversation_history) > 10:  # Keep last 10 messages
            self.conversation_history.pop(0)
            
    def add_action(self, action_type, target=None, reason=None):
        """Add action to memory"""
        self.actions_taken.append({
            "type": action_type,
            "target": target,
            "reason": reason,
            "round": len(self.actions_taken) + 1
        })
        if len(self.actions_taken) > 5:  # Keep last 5 actions
            self.actions_taken.pop(0)

# Global memory for all AI agents
ai_memory = AIMemory()

# ---------------------------------------
# PROVIDER ROUTER
# ---------------------------------------
async def call_ai(role, name, alive, memory):
    """
    Call AI provider or use intelligent fallback
    """
    
    provider = select_provider(name)
    
    # Remove the calling AI from targets if they're in the list
    targets = [p for p in alive if p != name]
    
    if not targets:
        # If no targets available, return a safe default
        return {
            "target": random.choice(alive),
            "reason": "No other targets available"
        }
    
    # Build context for AI decision
    context = build_ai_context(role, name, alive, memory)
    
    try:
        if provider == "openai" and HAS_OPENAI:
            return await call_openai(context)
        elif provider == "gemini" and HAS_GEMINI:
            return await call_gemini(context)
        elif provider == "groq" and HAS_GROQ:
            return await call_groq(context)
        elif provider == "mistral" and HAS_MISTRAL:
            return await call_mistral(context)
        else:
            # Use intelligent fallback
            return intelligent_fallback(role, name, alive, memory)
            
    except Exception as e:
        print(f"AI call failed, using fallback: {e}")
        # Use intelligent fallback
        return intelligent_fallback(role, name, alive, memory)

# ---------------------------------------
# CONTEXT BUILDER
# ---------------------------------------
def build_ai_context(role, name, alive, memory):
    """Build context for AI decision making"""
    
    # Basic context
    context = f"""
Your role: {role}
Your name: {name}
Alive players: {', '.join(alive)}

Current game state:
"""
    
    # Add memory context if available
    if memory and hasattr(memory, 'suspicion_levels'):
        context += "\nSuspicion levels:\n"
        for player, level in memory.suspicion_levels.items():
            if player in alive:
                context += f"- {player}: {level}/10 suspicion\n"
    
    if memory and hasattr(memory, 'actions_taken'):
        context += "\nRecent actions:\n"
        for action in memory.actions_taken[-3:]:  # Last 3 actions
            context += f"- {action['type']} {action.get('target', '')}: {action.get('reason', '')}\n"
    
    # Role-specific instructions
    context += f"\n{get_role_instructions(role)}"
    
    return context

# ---------------------------------------
# ROLE-SPECIFIC INSTRUCTIONS
# ---------------------------------------
def get_role_instructions(role):
    """Get role-specific instructions for AI"""
    
    instructions = {
        "mafia": """
As Mafia, your goal is to eliminate civilians and blend in.
Strategy:
- Target civilians first, they are the biggest threat
- Avoid targeting the doctor if possible
- Try to frame other players during discussions
- Be subtle in your accusations
""",
        "doctor": """
As Doctor, your goal is to protect players and find the mafia.
Strategy:
- Save players who seem important or are being targeted
- Try to deduce who the mafia might be
- Protect the sheriff if you can identify them
- Don't reveal your role too early
""",
        "sheriff": """
As Sheriff, your goal is to investigate and find the mafia.
Strategy:
- Investigate suspicious players
- Share your findings carefully
- Try to build trust with other players
- Be cautious about accusing without evidence
""",
        "civilian": """
As Civilian, your goal is to find and eliminate the mafia.
Strategy:
- Observe player behavior carefully
- Look for inconsistencies in stories
- Vote strategically based on discussions
- Try to protect other civilians
"""
    }
    
    return instructions.get(role, "Make the best decision for your role.")

# ---------------------------------------
# INTELLIGENT FALLBACK
# ---------------------------------------
def intelligent_fallback(role, name, alive, memory):
    """
    Intelligent fallback that simulates AI behavior
    Uses memory and game context for better decisions
    """
    
    # Remove the calling AI from targets
    targets = [p for p in alive if p != name]
    
    if role == "mafia":
        return mafia_fallback(name, targets, memory)
    elif role == "doctor":
        return doctor_fallback(name, targets, memory)
    elif role == "sheriff":
        return sheriff_fallback(name, targets, memory)
    elif role == "civilian":
        return civilian_fallback(name, targets, memory)
    else:
        return default_fallback(targets)

def mafia_fallback(name, targets, memory):
    """Mafia-specific fallback logic"""
    
    # Mafia strategy: target most suspicious civilians first
    if memory and hasattr(memory, 'suspicion_levels'):
        # Target players with low suspicion (civilians likely to be trusted)
        suspicion_scores = []
        for player in targets:
            suspicion = memory.suspicion_levels.get(player, 0)
            # Mafia prefers players with low suspicion (less likely to be important)
            score = 10 - suspicion  # Higher score = better target
            suspicion_scores.append((player, score))
        
        # Sort by score (highest first)
        suspicion_scores.sort(key=lambda x: x[1], reverse=True)
        potential_targets = [player for player, score in suspicion_scores]
    else:
        potential_targets = targets
    
    # Add some randomness
    target = random.choice(potential_targets[:3]) if len(potential_targets) >= 3 else random.choice(potential_targets)
    
    reasons = [
        f"{target} has been too quiet and might be easily eliminated",
        f"I suspect {target} is gaining too much trust",
        f"{target} seems vulnerable and won't be missed",
        f"Eliminating {target} will help us blend in better",
        f"{target} hasn't contributed much to discussions",
        f"I need to reduce civilian numbers, starting with {target}"
    ]
    
    return {
        "target": target,
        "reason": random.choice(reasons)
    }

def doctor_fallback(name, targets, memory):
    """Doctor-specific fallback logic"""
    
    # Doctor strategy: save players who are most suspected or important
    if memory and hasattr(memory, 'suspicion_levels'):
        # Save players with high suspicion (likely to be targeted)
        suspicion_scores = []
        for player in targets:
            suspicion = memory.suspicion_levels.get(player, 0)
            suspicion_scores.append((player, suspicion))
        
        # Sort by suspicion (highest first)
        suspicion_scores.sort(key=lambda x: x[1], reverse=True)
        potential_targets = [player for player, score in suspicion_scores]
    else:
        potential_targets = targets
    
    # Add some randomness but prefer high-suspicion players
    if len(potential_targets) >= 2:
        target = random.choice(potential_targets[:2])
    else:
        target = random.choice(potential_targets)
    
    reasons = [
        f"{target} seems like a key player who needs protection",
        f"I want to protect {target} as they might be targeted",
        f"{target} has been helpful and should be saved",
        f"Saving {target} could change the game outcome",
        f"{target} appears to be in danger based on discussions",
        f"I believe {target} is important for our team's success"
    ]
    
    return {
        "target": target,
        "reason": random.choice(reasons)
    }

def sheriff_fallback(name, targets, memory):
    """Sheriff-specific fallback logic"""
    
    # Sheriff strategy: investigate most suspicious players
    if memory and hasattr(memory, 'suspicion_levels'):
        # Investigate players with highest suspicion
        suspicion_scores = []
        for player in targets:
            suspicion = memory.suspicion_levels.get(player, 0)
            suspicion_scores.append((player, suspicion))
        
        # Sort by suspicion (highest first)
        suspicion_scores.sort(key=lambda x: x[1], reverse=True)
        potential_targets = [player for player, score in suspicion_scores]
    else:
        potential_targets = targets
    
    # Sheriff should focus on most suspicious players
    target = potential_targets[0] if potential_targets else random.choice(targets)
    
    reasons = [
        f"{target} seems suspicious based on their behavior",
        f"I think {target} might be the mafia",
        f"{target} has been acting strangely during discussions",
        f"My investigation points to {target} as a potential threat",
        f"{target} avoided answering important questions",
        f"I need to investigate {target} more closely"
    ]
    
    return {
        "target": target,
        "reason": random.choice(reasons)
    }

def civilian_fallback(name, targets, memory):
    """Civilian-specific fallback logic"""
    
    # Civilian strategy: accuse most suspicious players
    if memory and hasattr(memory, 'suspicion_levels'):
        # Accuse players with highest suspicion
        suspicion_scores = []
        for player in targets:
            suspicion = memory.suspicion_levels.get(player, 0)
            suspicion_scores.append((player, suspicion))
        
        # Sort by suspicion (highest first)
        suspicion_scores.sort(key=lambda x: x[1], reverse=True)
        potential_targets = [player for player, score in suspicion_scores]
    else:
        potential_targets = targets
    
    # Civilians should focus on most suspicious players
    if len(potential_targets) >= 2:
        target = random.choice(potential_targets[:2])
    else:
        target = random.choice(potential_targets)
    
    reasons = [
        f"{target} has been too quiet during discussions",
        f"I think {target} is hiding something",
        f"{target} seems nervous and suspicious",
        f"Something about {target} doesn't feel right",
        f"{target} avoided answering my questions",
        f"I suspect {target} based on their behavior patterns",
        f"{target} changed their story multiple times",
        f"I noticed {target} acting differently from others"
    ]
    
    return {
        "target": target,
        "reason": random.choice(reasons)
    }

def default_fallback(targets):
    """Default fallback for unknown roles"""
    return {
        "target": random.choice(targets),
        "reason": "Default reasoning based on game context"
    }

# ---------------------------------------
# REAL AI INTEGRATION
# ---------------------------------------
async def call_openai(context):
    """Call OpenAI API"""
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        raise

async def call_gemini(context):
    """Call Google Gemini API"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = await model.generate_content_async(
            SYSTEM_PROMPT + "\n" + context
        )
        
        result = response.text
        return json.loads(result)
        
    except Exception as e:
        print(f"Gemini error: {e}")
        raise

async def call_groq(context):
    """Call Groq API"""
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
        
    except Exception as e:
        print(f"Groq error: {e}")
        raise

async def call_mistral(context):
    """Call Mistral API"""
    try:
        response = await mistral_client.chat(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
        
    except Exception as e:
        print(f"Mistral error: {e}")
        raise

# ---------------------------------------
# PROVIDER SELECTION (YOU CAN CHANGE)
# ---------------------------------------
def select_provider(name):
    """Select AI provider for each player"""
    return {
        "AI1": "openai",
        "AI2": "gemini",
        "AI3": "groq",
        "AI4": "mistral",
        "AI5": "openai",
        "AI6": "groq",
    }.get(name, "openai")

# ---------------------------------------
# MEMORY MANAGEMENT
# ---------------------------------------
def update_suspicion_levels(players, amounts):
    """Update suspicion levels for multiple players"""
    for player, amount in zip(players, amounts):
        ai_memory.update_suspicion(player, amount)

def get_suspicion_report():
    """Get current suspicion levels"""
    return ai_memory.suspicion_levels

def reset_memory():
    """Reset AI memory for new game"""
    global ai_memory
    ai_memory = AIMemory()

# ---------------------------------------
# ADMIN FUNCTIONS
# ---------------------------------------
def get_ai_status():
    """Get status of AI providers"""
    return {
        "openai": HAS_OPENAI,
        "gemini": HAS_GEMINI,
        "groq": HAS_GROQ,
        "mistral": HAS_MISTRAL,
        "real_ai_available": real_ai_available
    }

def get_provider_assignment():
    """Get provider assignments for each AI"""
    assignments = {}
    for ai_name in ["AI1", "AI2", "AI3", "AI4", "AI5", "AI6"]:
        assignments[ai_name] = select_provider(ai_name)
    return assignments