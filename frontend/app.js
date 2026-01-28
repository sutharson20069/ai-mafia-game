const players = ["AI1", "AI2", "AI3", "AI4", "AI5", "AI6"];
const logBox = document.getElementById("logBox");
const playersList = document.getElementById("players");
const statusBadge = document.getElementById("gameStatus");

function renderPlayers() {
  playersList.innerHTML = "";
  players.forEach(p => {
    const li = document.createElement("li");
    li.className = "list-group-item bg-dark text-light d-flex justify-content-between";
    li.innerHTML = `<span>${p}</span><span class="text-success">Alive</span>`;
    playersList.appendChild(li);
  });
}

function addLog(text) {
  const div = document.createElement("div");
  div.className = "log-entry";
  div.innerText = text;
  logBox.appendChild(div);
  logBox.scrollTop = logBox.scrollHeight;
}

function startGame() {
  statusBadge.innerText = "Running";
  statusBadge.className = "badge bg-success";
  logBox.innerHTML = "";
  renderPlayers();

  addLog("🌙 Night begins...");
  addLog("🧠 Mafia thinks: I should eliminate AI3 because it stayed silent.");
  addLog("🛡 Doctor thinks: I will save AI3 because they may be targeted.");
  addLog("🕵 Sheriff thinks: I suspect AI4 due to voting behavior.");
}

function nextPhase() {
  addLog("☀ Day discussion starts...");
  addLog("💬 AI1: AI4 feels suspicious.");
  addLog("💬 AI2: I agree, AI4 defended too much.");
  addLog("🗳 Voting in progress...");
  addLog("❌ AI4 eliminated.");
}

function resetGame() {
  statusBadge.innerText = "Waiting";
  statusBadge.className = "badge bg-secondary";
  logBox.innerHTML = "";
}
