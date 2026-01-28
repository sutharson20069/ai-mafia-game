"""
Simplified AI Clients for AI Mafia Game
This version works without external API dependencies
"""

import random
import json

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

# ---------------------------------------
# PROVIDER ROUTER
# ---------------------------------------
async def call_ai(role, name, alive, memory):
    """
    Simulated AI call that works without external APIs
    Each AI role has different behavior logic
    """
    
    # Remove the calling AI from targets if they're in the list
    targets = [p for p in alive if p != name]
    
    if not targets:
        # If no targets available, return a safe default
        return {
            "target": random.choice(alive),
            "reason": "No other targets available"
        }
    
    # Different logic for each role
    if role == "mafia":
        # Mafia tries to eliminate civilians first, then sheriff, avoids doctor
        potential_targets = []
        
        # Prefer civilians
        civilians = [p for p in targets if p.startswith("AI")]  # Simple heuristic
        if civilians:
            potential_targets.extend(civilians)
        
        # If no civilians, target anyone
        if not potential_targets:
            potential_targets = targets
        
        target = random.choice(potential_targets)
        
        reasons = [
            f"{target} has been too quiet",
            f"I suspect {target} is the sheriff",
            f"{target} seems vulnerable",
            f"Eliminating {target} will help us win",
            f"{target} questioned me earlier"
        ]
        
        return {
            "target": target,
            "reason": random.choice(reasons)
        }
    
    elif role == "doctor":
        # Doctor tries to save important roles or random players
        potential_targets = []
        
        # Try to save players who might be important
        important_players = [p for p in targets if any(keyword in p.lower() for keyword in ['1', '2', 'sheriff'])]
        if important_players:
            potential_targets.extend(important_players)
        
        # If no important players, save anyone
        if not potential_targets:
            potential_targets = targets
        
        target = random.choice(potential_targets)
        
        reasons = [
            f"{target} seems like a key player",
            f"I want to protect {target}",
            f"{target} might be targeted by mafia",
            f"Saving {target} could change the game",
            f"{target} has been helpful"
        ]
        
        return {
            "target": target,
            "reason": random.choice(reasons)
        }
    
    elif role == "sheriff":
        # Sheriff tries to find mafia
        potential_targets = targets
        
        target = random.choice(potential_targets)
        
        reasons = [
            f"{target} seems suspicious",
            f"I think {target} might be mafia",
            f"{target} has been acting strangely",
            f"My investigation points to {target}",
            f"{target} avoided my questions"
        ]
        
        return {
            "target": target,
            "reason": random.choice(reasons)
        }
    
    elif role == "civilian":
        # Civilians try to find mafia based on behavior
        potential_targets = targets
        
        target = random.choice(potential_targets)
        
        reasons = [
            f"{target} has been too quiet",
            f"I think {target} is hiding something",
            f"{target} seems nervous",
            f"Something about {target} doesn't feel right",
            f"{target} avoided answering questions"
        ]
        
        return {
            "target": target,
            "reason": random.choice(reasons)
        }
    
    else:
        # Default fallback
        return {
            "target": random.choice(targets),
            "reason": "Default reasoning"
        }

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