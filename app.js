let socket = null;

function addLog(text) {
  const logBox = document.getElementById("logBox");
  const div = document.createElement("div");
  div.className = "log-entry";
  div.innerText = text;
  logBox.appendChild(div);
  logBox.scrollTop = logBox.scrollHeight;
}

function startGame() {
  const status = document.getElementById("gameStatus");
  status.innerText = "Running";
  status.className = "badge bg-success";

  document.getElementById("logBox").innerHTML = "";

  if (socket) socket.close();

  socket = new WebSocket("ws://127.0.0.1:8000/ws");

  socket.onopen = () => {
    addLog("🔌 Connected to game server");
  };

  socket.onmessage = (event) => {
    addLog(event.data);
  };

  socket.onerror = () => {
    addLog("❌ WebSocket error");
  };

  socket.onclose = () => {
    addLog("🔌 Connection closed");
  };
}
