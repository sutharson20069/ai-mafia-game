import random
from ai_clients import call_ai

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
            m = await call_ai("mafia", mafia, self.alive(), [])
            mafia_target = m['target']
            mafia_reason = m['reason']
        except Exception as e:
            # Fallback: mafia targets a random civilian
            mafia_target = random.choice([p for p in self.alive() if self.state[p]["role"] == "civilian"])
            mafia_reason = f"I suspect {mafia_target} because they seem vulnerable"

        await send(f"[MAFIA] Mafia ({mafia}) thinks: I eliminate {mafia_target} because {mafia_reason}")

        try:
            d = await call_ai("doctor", doctor, self.alive(), [])
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

        try:
            s = await call_ai("sheriff", sheriff, self.alive(), [])
            sheriff_target = s['target']
        except Exception as e:
            # Fallback: sheriff suspects a random player
            sheriff_target = random.choice(self.alive())

        await send(f"[SHERIFF] Sheriff ({sheriff}) suspects {sheriff_target}")

        # Resolve night actions
        if mafia_target != doctor_target:
            self.state[mafia_target]["alive"] = False
            await send(f"[KILL] {mafia_target} was killed by the mafia")
        else:
            await send("[SAVE] Doctor saved the target from the mafia")

        return sheriff_target

    async def day(self, suspect, send):
        await send("[DAY] Day discussion starts")

        # Day discussion with AI or fallback
        for p in self.alive():
            try:
                res = await call_ai("civilian", p, self.alive(), [])
                target = res['target']
                reason = res['reason']
            except Exception as e:
                # Fallback: each player accuses someone randomly
                target = random.choice(self.alive())
                reason = f"I think {target} is acting suspiciously"

            await send(f"[CHAT] {p}: I think {target} is suspicious because {reason}")

        # Voting phase
        votes = {}
        for p in self.alive():
            # Players tend to vote for the sheriff's suspect or random
            if random.random() > 0.7 and suspect in self.alive():  # 70% chance to follow sheriff
                v = suspect
            else:
                v = random.choice(self.alive())
            votes[v] = votes.get(v, 0) + 1

        eliminated = max(votes, key=votes.get)
        self.state[eliminated]["alive"] = False
        await send(f"[VOTE] Voting complete — {eliminated} eliminated with {votes[eliminated]} votes")

    def mafia_wins(self):
        mafia = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]=="mafia")
        civ = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]!="mafia")
        return mafia >= civ

    def civilians_win(self):
        mafia = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]=="mafia")
        return mafia == 0