import random
from ai_clients import call_ai, update_suspicion_levels, reset_memory, get_suspicion_report

class MafiaGame:
    def __init__(self):
        self.players = ["AI1","AI2","AI3","AI4","AI5","AI6"]
        roles = ["mafia","doctor","sheriff","civilian","civilian","civilian"]
        random.shuffle(roles)

        self.state = {
            p: {"role": r, "alive": True}
            for p, r in zip(self.players, roles)
        }

        self.last_saved = None
        self.round = 1
        self.game_history = []
        
        # Reset memory for new game
        reset_memory()

    def alive(self):
        return [p for p in self.state if self.state[p]["alive"]]

    def get_player(self, role):
        return next(p for p in self.alive() if self.state[p]["role"] == role)

    async def night(self, send):
        await send(f"[NIGHT] Night {self.round} begins")

        mafia = self.get_player("mafia")
        doctor = self.get_player("doctor")
        sheriff = self.get_player("sheriff")

        # Try AI calls with fallback
        try:
            m = await call_ai("mafia", mafia, self.alive(), None)
            mafia_target = m['target']
            mafia_reason = m['reason']
        except Exception as e:
            # Fallback: mafia targets a random civilian
            mafia_target = random.choice([p for p in self.alive() if self.state[p]["role"] == "civilian"])
            mafia_reason = f"I suspect {mafia_target} because they seem vulnerable"

        await send(f"[MAFIA] Mafia ({mafia}) thinks: I eliminate {mafia_target} because {mafia_reason}")

        # Update suspicion based on mafia's reasoning
        if "suspicious" in mafia_reason.lower() or "quiet" in mafia_reason.lower():
            update_suspicion_levels([mafia_target], [2])  # Increase suspicion

        try:
            d = await call_ai("doctor", doctor, self.alive(), None)
            if d["target"] == self.last_saved:
                d["target"] = random.choice(self.alive())
            doctor_target = d["target"]
            doctor_reason = d["reason"]
        except Exception as e:
            # Fallback: doctor saves a random player (not mafia)
            doctor_target = random.choice([p for p in self.alive() if self.state[p]["role"] != "mafia"])
            doctor_reason = f"I want to protect {doctor_target} as they seem important"

        self.last_saved = doctor_target
        await send(f"[DOCTOR] Doctor ({doctor}) thinks: I save {doctor_target} because {doctor_reason}")

        # Update suspicion based on doctor's reasoning
        if "protect" in doctor_reason.lower() or "important" in doctor_reason.lower():
            update_suspicion_levels([doctor_target], [-1])  # Decrease suspicion

        try:
            s = await call_ai("sheriff", sheriff, self.alive(), None)
            sheriff_target = s['target']
        except Exception as e:
            # Fallback: sheriff suspects a random player
            sheriff_target = random.choice(self.alive())

        await send(f"[SHERIFF] Sheriff ({sheriff}) suspects {sheriff_target}")

        # Update suspicion based on sheriff's investigation
        update_suspicion_levels([sheriff_target], [3])  # Significant suspicion increase

        # Resolve night actions
        if mafia_target != doctor_target:
            self.state[mafia_target]["alive"] = False
            await send(f"[KILL] {mafia_target} was killed by the mafia")
            
            # Record the kill in game history
            self.game_history.append({
                "round": self.round,
                "phase": "night",
                "action": "kill",
                "target": mafia_target,
                "by": mafia
            })
        else:
            await send("[SAVE] Doctor saved the target from the mafia")
            
            # Record the save in game history
            self.game_history.append({
                "round": self.round,
                "phase": "night",
                "action": "save",
                "target": doctor_target,
                "by": doctor
            })

        return sheriff_target

    async def day(self, suspect, send):
        await send("[DAY] Day discussion starts")

        # Get current suspicion levels
        suspicion_report = get_suspicion_report()
        
        # Day discussion with AI or fallback
        for p in self.alive():
            try:
                res = await call_ai("civilian", p, self.alive(), None)
                target = res['target']
                reason = res['reason']
            except Exception as e:
                # Fallback: each player accuses someone based on suspicion levels
                if suspicion_report:
                    # Sort players by suspicion level (highest first)
                    sorted_players = sorted(
                        suspicion_report.items(), 
                        key=lambda x: x[1], 
                        reverse=True
                    )
                    # Choose from top 3 most suspicious players
                    top_suspicious = [player for player, level in sorted_players[:3] if player in self.alive()]
                    target = random.choice(top_suspicious) if top_suspicious else random.choice(self.alive())
                else:
                    target = random.choice(self.alive())
                
                reason = f"I think {target} is acting suspiciously"

            await send(f"[CHAT] {p}: I think {target} is suspicious because {reason}")

            # Update suspicion based on accusation
            if p != target:  # Don't update if player is accusing themselves
                suspicion_increase = 1
                if "mafia" in reason.lower() or "lying" in reason.lower():
                    suspicion_increase = 2
                update_suspicion_levels([target], [suspicion_increase])

        # Get updated suspicion levels for voting
        suspicion_report = get_suspicion_report()
        
        # Voting phase with advanced logic
        votes = {}
        for p in self.alive():
            # Players tend to vote for the sheriff's suspect or most suspicious players
            if random.random() > 0.6 and suspect in self.alive():  # 60% chance to follow sheriff
                v = suspect
            elif suspicion_report:
                # 30% chance to vote for most suspicious player
                sorted_players = sorted(
                    suspicion_report.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                top_suspicious = [player for player, level in sorted_players if player in self.alive()]
                if top_suspicious:
                    v = random.choice(top_suspicious[:2])  # Choose from top 2 most suspicious
                else:
                    v = random.choice(self.alive())
            else:
                v = random.choice(self.alive())
            
            votes[v] = votes.get(v, 0) + 1

        eliminated = max(votes, key=votes.get)
        self.state[eliminated]["alive"] = False
        await send(f"[VOTE] Voting complete — {eliminated} eliminated with {votes[eliminated]} votes")
        
        # Record the elimination in game history
        self.game_history.append({
            "round": self.round,
            "phase": "day",
            "action": "eliminate",
            "target": eliminated,
            "votes": votes[eliminated]
        })

    def mafia_wins(self):
        mafia = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]=="mafia")
        civ = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]!="mafia")
        return mafia >= civ

    def civilians_win(self):
        mafia = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]=="mafia")
        return mafia == 0
        
    def get_game_summary(self):
        """Get summary of the game so far"""
        summary = {
            "round": self.round,
            "players_alive": len(self.alive()),
            "players_eliminated": len(self.players) - len(self.alive()),
            "history": self.game_history[-5:],  # Last 5 events
            "suspicion_levels": get_suspicion_report()
        }
        return summary
        
    def get_player_roles(self):
        """Get roles of all players (for admin/debug)"""
        return {p: self.state[p]["role"] for p in self.players}