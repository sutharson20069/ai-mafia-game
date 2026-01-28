#!/usr/bin/env python3

"""
Test script for AI Mafia Game
This script tests the game logic without requiring AI API calls
"""

import asyncio
from game_logic import MafiaGame

async def test_game():
    print("Testing AI Mafia Game Logic")
    print("=" * 40)
    
    # Create game instance
    game = MafiaGame()
    
    print(f"Initial players: {game.players}")
    print(f"Initial roles: {[game.state[p]['role'] for p in game.players]}")
    print(f"Alive players: {game.alive()}")
    
    # Test night phase
    print("\nTesting Night Phase:")
    
    async def mock_send(message):
        print(f"  {message}")
    
    try:
        suspect = await game.night(mock_send)
        print(f"Sheriff suspects: {suspect}")
        print(f"Players alive after night: {game.alive()}")
        
        # Test day phase
        print("\nTesting Day Phase:")
        await game.day(suspect, mock_send)
        print(f"Players alive after day: {game.alive()}")
        
        # Test win conditions
        print(f"\nMafia wins: {game.mafia_wins()}")
        print(f"Civilians win: {game.civilians_win()}")
        
        print("\nGame logic test completed successfully!")
        
    except Exception as e:
        print(f"\nError during game test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_game())