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
        await send(f"🌙 Night {self.round} begins")

        mafia = self.get_player("mafia")
        doctor = self.get_player("doctor")
        sheriff = self.get_player("sheriff")

        m = await call_ai("mafia", mafia, self.alive(), [])
        await send(f"🧠 Mafia thinks: I eliminate {m['target']} because {m['reason']}")

        d = await call_ai("doctor", doctor, self.alive(), [])
        if d["target"] == self.last_saved:
            d["target"] = random.choice(self.alive())
        self.last_saved = d["target"]
        await send(f"🛡 Doctor thinks: I save {d['target']} because {d['reason']}")

        s = await call_ai("sheriff", sheriff, self.alive(), [])
        await send(f"📢 Anonymous suspects {s['target']}")

        if m["target"] != d["target"]:
            self.state[m["target"]]["alive"] = False
            await send(f"☠ {m['target']} was killed")
        else:
            await send("✨ Doctor saved the target")

        return s["target"]

    async def day(self, suspect, send):
        await send("☀ Day discussion starts")

        for p in self.alive():
            res = await call_ai("civilian", p, self.alive(), [])
            await send(f"💬 {p}: I think {res['target']} is suspicious")

        votes = {}
        for p in self.alive():
            v = random.choice(self.alive())
            votes[v] = votes.get(v, 0) + 1

        eliminated = max(votes, key=votes.get)
        self.state[eliminated]["alive"] = False
        await send(f"🗳 Voting complete — {eliminated} eliminated")

    def mafia_wins(self):
        mafia = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]=="mafia")
        civ = sum(1 for p in self.state if self.state[p]["alive"] and self.state[p]["role"]!="mafia")
        return mafia >= civ
