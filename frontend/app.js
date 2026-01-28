// Enhanced AI Mafia Game Frontend
// Global variables
const players = ["AI1", "AI2", "AI3", "AI4", "AI5", "AI6"];
const logBox = document.getElementById("logBox");
const playersList = document.getElementById("players");
const statusBadge = document.getElementById("gameStatus");
const aiStatusBadge = document.getElementById("aiStatus");
const aiProviderStatus = document.getElementById("aiProviderStatus");

// Game state
let gameState = {
  players: {},
  round: 1,
  phase: "waiting",
  paused: false,
  rolesRevealed: false,
  suspicionLevels: {}
};

// WebSocket connection
let socket = null;
let gameActive = false;

// Initialize the game
function initGame() {
  renderPlayers();
  updateGameStats();
  checkAIStatus();
  
  // Set up event listeners
  document.getElementById("toggleRolesBtn").addEventListener("click", toggleRoles);
}

// Render players with enhanced UI
function renderPlayers() {
  playersList.innerHTML = "";
  
  players.forEach(p => {
    const li = document.createElement("li");
    li.className = "list-group-item d-flex justify-content-between align-items-center";
    
    // Player info
    const playerInfo = document.createElement("div");
    playerInfo.innerHTML = `
      <strong>${p}</strong>
      <div class="suspicion-meter mt-1">
        <div class="suspicion-fill" style="width: 0%" id="suspicion-${p}"></div>
      </div>
    `;
    
    // Status
    const statusSpan = document.createElement("span");
    statusSpan.className = "player-alive";
    statusSpan.id = `status-${p}`;
    statusSpan.textContent = "Alive";
    
    // Role badge (hidden by default)
    const roleBadge = document.createElement("span");
    roleBadge.className = "badge bg-primary role-badge ms-2";
    roleBadge.id = `role-${p}`;
    roleBadge.textContent = "Unknown";
    roleBadge.style.display = "none";
    
    li.appendChild(playerInfo);
    li.appendChild(roleBadge);
    li.appendChild(statusSpan);
    playersList.appendChild(li);
  });
}

// Add log entry with enhanced formatting
function addLog(text) {
  const div = document.createElement("div");
  div.className = "log-entry";
  
  // Parse and format different log types
  if (text.startsWith("[NIGHT]")) {
    div.style.color = "#2196F3";
  } else if (text.startsWith("[MAFIA]")) {
    div.style.color = "#F44336";
  } else if (text.startsWith("[DOCTOR]")) {
    div.style.color = "#4CAF50";
  } else if (text.startsWith("[SHERIFF]")) {
    div.style.color = "#FF9800";
  } else if (text.startsWith("[DAY]")) {
    div.style.color = "#FFEB3B";
  } else if (text.startsWith("[CHAT]")) {
    div.style.color = "#9C27B0";
  } else if (text.startsWith("[VOTE]")) {
    div.style.color = "#00BCD4";
  } else if (text.startsWith("[KILL]")) {
    div.style.color = "#F44336";
    div.style.fontWeight = "bold";
  } else if (text.startsWith("[SAVE]")) {
    div.style.color = "#4CAF50";
    div.style.fontWeight = "bold";
  } else if (text.startsWith("[END]")) {
    div.style.color = "#FF5722";
    div.style.fontWeight = "bold";
    div.style.fontSize = "1.1em";
  }
  
  div.innerText = text;
  logBox.appendChild(div);
  logBox.scrollTop = logBox.scrollHeight;
  
  // Parse game events
  parseGameEvent(text);
}

// Parse game events and update UI
function parseGameEvent(text) {
  if (text.startsWith("[NIGHT]")) {
    gameState.phase = "night";
  } else if (text.startsWith("[DAY]")) {
    gameState.phase = "day";
  } else if (text.includes("Round")) {
    const roundMatch = text.match(/Round (\d+)/);
    if (roundMatch) {
      gameState.round = parseInt(roundMatch[1]);
      updateGameStats();
    }
  } else if (text.includes("was killed")) {
    const playerMatch = text.match(/(\w+) was killed/);
    if (playerMatch) {
      const player = playerMatch[1];
      updatePlayerStatus(player, "Dead");
      updateGameStats();
    }
  } else if (text.includes("eliminated")) {
    const playerMatch = text.match(/eliminated — (\w+)/);
    if (playerMatch) {
      const player = playerMatch[1];
      updatePlayerStatus(player, "Dead");
      updateGameStats();
    }
  } else if (text.includes("suspects")) {
    const match = text.match(/suspects (\w+)/);
    if (match) {
      const suspectedPlayer = match[1];
      updateSuspicion(suspectedPlayer, 30); // Increase suspicion
    }
  } else if (text.includes("suspicious because")) {
    const match = text.match(/I think (\w+) is suspicious/);
    if (match) {
      const suspectedPlayer = match[1];
      updateSuspicion(suspectedPlayer, 15); // Increase suspicion
    }
  }
}

// Update player status
function updatePlayerStatus(player, status) {
  const statusElement = document.getElementById(`status-${player}`);
  if (statusElement) {
    statusElement.textContent = status;
    statusElement.className = status === "Alive" ? "player-alive" : "player-dead";
  }
}

// Update suspicion meter
function updateSuspicion(player, amount) {
  const suspicionElement = document.getElementById(`suspicion-${player}`);
  if (suspicionElement) {
    let currentWidth = parseInt(suspicionElement.style.width || "0%") || 0;
    let newWidth = Math.min(100, currentWidth + amount);
    suspicionElement.style.width = `${newWidth}%`;
    
    // Update suspicion levels in game state
    gameState.suspicionLevels[player] = newWidth;
  }
}

// Update game statistics
function updateGameStats() {
  const aliveCount = players.filter(p => {
    const statusElement = document.getElementById(`status-${p}`);
    return statusElement && statusElement.textContent === "Alive";
  }).length;
  
  document.getElementById("playersAlive").textContent = aliveCount;
  document.getElementById("roundNumber").textContent = gameState.round;
  
  // Estimate mafia and civilian counts (these are estimates since roles are hidden)
  document.getElementById("mafiaCount").textContent = gameActive ? "1" : "0";
  document.getElementById("civilianCount").textContent = aliveCount - 1;
}

// Start the game
function startGame() {
  if (gameActive) return;
  
  gameActive = true;
  gameState.round = 1;
  gameState.phase = "night";
  gameState.suspicionLevels = {};
  
  statusBadge.innerText = "Running";
  statusBadge.className = "badge bg-success";
  
  logBox.innerHTML = "";
  renderPlayers();
  updateGameStats();
  
  // Reset suspicion meters
  players.forEach(p => {
    const suspicionElement = document.getElementById(`suspicion-${p}`);
    if (suspicionElement) {
      suspicionElement.style.width = "0%";
    }
    updatePlayerStatus(p, "Alive");
  });
  
  addLog("[CONNECT] Connecting to game server...");
  
  // Connect WebSocket
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const hostname = window.location.hostname;
  const port = window.location.port ? ":" + window.location.port : "";
  const wsUrl = `${protocol}//${hostname}${port}/ws`;
  
  socket = new WebSocket(wsUrl);
  
  socket.onopen = function() {
    addLog("[CONNECT] Connected to game server");
    addLog("[START] Game starting...");
  };
  
  socket.onmessage = function(event) {
    addLog(event.data);
    
    // Check for game end conditions
    if (event.data.includes("GAME OVER")) {
      gameActive = false;
      statusBadge.innerText = "Game Over";
      statusBadge.className = "badge bg-danger";
    }
  };
  
  socket.onclose = function() {
    addLog("[DISCONNECT] Disconnected from game server");
    gameActive = false;
    statusBadge.innerText = "Disconnected";
    statusBadge.className = "badge bg-danger";
  };
  
  socket.onerror = function(error) {
    addLog("[ERROR] WebSocket error: " + error.message);
    gameActive = false;
    statusBadge.innerText = "Error";
    statusBadge.className = "badge bg-danger";
  };
}

// Pause the game
function pauseGame() {
  if (!gameActive || !socket) return;
  
  gameState.paused = !gameState.paused;
  
  if (gameState.paused) {
    addLog("[PAUSE] Game paused");
    statusBadge.innerText = "Paused";
    statusBadge.className = "badge bg-warning";
  } else {
    addLog("[RESUME] Game resumed");
    statusBadge.innerText = "Running";
    statusBadge.className = "badge bg-success";
  }
}

// Step through the game (one phase at a time)
function stepGame() {
  if (!gameActive || !socket) return;
  
  // This would require server-side support
  addLog("[INFO] Step function would require server-side implementation");
}

// Reset the game
function resetGame() {
  gameActive = false;
  gameState = {
    players: {},
    round: 1,
    phase: "waiting",
    paused: false,
    rolesRevealed: false,
    suspicionLevels: {}
  };
  
  statusBadge.innerText = "Waiting";
  statusBadge.className = "badge bg-secondary";
  
  logBox.innerHTML = "";
  renderPlayers();
  updateGameStats();
  
  // Close WebSocket if open
  if (socket) {
    socket.close();
    socket = null;
  }
}

// Toggle role visibility
function toggleRoles() {
  gameState.rolesRevealed = !gameState.rolesRevealed;
  
  const button = document.getElementById("toggleRolesBtn");
  const icon = button.querySelector("i");
  
  if (gameState.rolesRevealed) {
    icon.className = "bi bi-eye-slash";
    button.textContent = " Hide Roles";
    
    // In a real implementation, you would fetch roles from the server
    // For now, we'll show placeholder roles
    const placeholderRoles = {
      "AI1": "Doctor",
      "AI2": "Mafia",
      "AI3": "Civilian",
      "AI4": "Sheriff",
      "AI5": "Civilian",
      "AI6": "Civilian"
    };
    
    players.forEach(p => {
      const roleElement = document.getElementById(`role-${p}`);
      if (roleElement) {
        roleElement.textContent = placeholderRoles[p] || "Unknown";
        roleElement.style.display = "inline-block";
        
        // Set role badge color
        if (placeholderRoles[p] === "Mafia") {
          roleElement.className = "badge bg-danger role-badge ms-2";
        } else if (placeholderRoles[p] === "Doctor") {
          roleElement.className = "badge bg-success role-badge ms-2";
        } else if (placeholderRoles[p] === "Sheriff") {
          roleElement.className = "badge bg-warning role-badge ms-2";
        } else {
          roleElement.className = "badge bg-info role-badge ms-2";
        }
      }
    });
  } else {
    icon.className = "bi bi-eye";
    button.textContent = " Show Roles";
    
    players.forEach(p => {
      const roleElement = document.getElementById(`role-${p}`);
      if (roleElement) {
        roleElement.style.display = "none";
      }
    });
  }
}

// Show player roles (admin function)
function showPlayerRoles() {
  // In a real implementation, this would fetch roles from the server
  // For demo purposes, we'll show the placeholder roles
  
  const modalContent = document.getElementById("playerRolesContent");
  modalContent.innerHTML = `
    <table class="table table-dark table-sm">
      <thead>
        <tr>
          <th>Player</th>
          <th>Role</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>AI1</td>
          <td><span class="badge bg-success">Doctor</span></td>
          <td id="modal-status-AI1">Alive</td>
        </tr>
        <tr>
          <td>AI2</td>
          <td><span class="badge bg-danger">Mafia</span></td>
          <td id="modal-status-AI2">Alive</td>
        </tr>
        <tr>
          <td>AI3</td>
          <td><span class="badge bg-info">Civilian</span></td>
          <td id="modal-status-AI3">Alive</td>
        </tr>
        <tr>
          <td>AI4</td>
          <td><span class="badge bg-warning">Sheriff</span></td>
          <td id="modal-status-AI4">Alive</td>
        </tr>
        <tr>
          <td>AI5</td>
          <td><span class="badge bg-info">Civilian</span></td>
          <td id="modal-status-AI5">Alive</td>
        </tr>
        <tr>
          <td>AI6</td>
          <td><span class="badge bg-info">Civilian</span></td>
          <td id="modal-status-AI6">Alive</td>
        </tr>
      </tbody>
    </table>
  `;
  
  // Update statuses from current game state
  players.forEach(p => {
    const statusElement = document.getElementById(`status-${p}`);
    const modalStatusElement = document.getElementById(`modal-status-${p}`);
    if (statusElement && modalStatusElement) {
      modalStatusElement.textContent = statusElement.textContent;
    }
  });
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("playerRolesModal"));
  modal.show();
}

// Show game summary
function showGameSummary() {
  const modalContent = document.getElementById("gameSummaryContent");
  
  // Get current game stats
  const aliveCount = players.filter(p => {
    const statusElement = document.getElementById(`status-${p}`);
    return statusElement && statusElement.textContent === "Alive";
  }).length;
  
  modalContent.innerHTML = `
    <div class="row g-3">
      <div class="col-md-6">
        <div class="card bg-secondary">
          <div class="card-header">Game Statistics</div>
          <div class="card-body">
            <p><strong>Current Round:</strong> ${gameState.round}</p>
            <p><strong>Players Alive:</strong> ${aliveCount}</p>
            <p><strong>Players Eliminated:</strong> ${6 - aliveCount}</p>
            <p><strong>Game Phase:</strong> ${gameState.phase}</p>
            <p><strong>Game Status:</strong> ${gameActive ? 'Active' : 'Inactive'}</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card bg-secondary">
          <div class="card-header">Suspicion Levels</div>
          <div class="card-body">
            ${players.map(p => {
              const suspicion = gameState.suspicionLevels[p] || 0;
              return `
                <div class="mb-2">
                  <strong>${p}:</strong>
                  <div class="suspicion-meter">
                    <div class="suspicion-fill" style="width: ${suspicion}%"></div>
                  </div>
                  <small>${suspicion}/100</small>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    </div>
    
    <div class="mt-3">
      <h6>Recent Game Events:</h6>
      <div class="card bg-secondary">
        <div class="card-body" style="max-height: 200px; overflow-y: auto;">
          ${gameState.phase === 'waiting' ? '<p>No game events yet. Start a game to see events.</p>' : '
            <p>[NIGHT] Night phase with mafia kills and doctor saves</p>
            <p>[DAY] Day discussions and voting</p>
            <p>[VOTE] Player eliminations based on voting</p>
          '}
        </div>
      </div>
    </div>
  `;
  
  // Show modal
  const modal = new bootstrap.Modal(document.getElementById("gameSummaryModal"));
  modal.show();
}

// Apply game settings
function applySettings() {
  const gameSpeed = document.getElementById("gameSpeed").value;
  const maxRounds = document.getElementById("maxRounds").value;
  
  addLog(`[SETTINGS] Game speed set to ${gameSpeed}x`);
  addLog(`[SETTINGS] Max rounds set to ${maxRounds}`);
  
  // In a real implementation, these would be sent to the server
  // For now, we'll just show a confirmation
  const toastElement = document.createElement('div');
  toastElement.className = 'position-fixed bottom-0 end-0 p-3';
  toastElement.style.zIndex = '11';
  toastElement.innerHTML = `
    <div class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          Settings applied successfully!
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;
  
  document.body.appendChild(toastElement);
  const toast = new bootstrap.Toast(toastElement.querySelector('.toast'));
  toast.show();
  
  // Remove toast after it disappears
  setTimeout(() => {
    toastElement.remove();
  }, 3000);
}

// Check AI provider status
function checkAIStatus() {
  // In a real implementation, this would fetch from the server
  // For now, we'll show a simulated status
  
  // Clear existing status
  aiProviderStatus.innerHTML = '';
  
  // Simulated AI provider status (would be fetched from server in real implementation)
  const providers = [
    { name: 'OpenAI', id: 'openai', active: false },
    { name: 'Gemini', id: 'gemini', active: false },
    { name: 'Groq', id: 'groq', active: false },
    { name: 'Mistral', id: 'mistral', active: false }
  ];
  
  providers.forEach(provider => {
    const col = document.createElement('div');
    col.className = 'col-6 col-md-3';
    
    const card = document.createElement('div');
    card.className = 'card bg-secondary';
    
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body text-center';
    
    const statusIndicator = document.createElement('div');
    statusIndicator.className = `status-indicator ${provider.active ? 'status-connected' : 'status-disconnected'}`;
    
    const providerName = document.createElement('small');
    providerName.textContent = provider.name;
    providerName.className = 'd-block mt-1';
    
    cardBody.appendChild(statusIndicator);
    cardBody.appendChild(providerName);
    card.appendChild(cardBody);
    col.appendChild(card);
    aiProviderStatus.appendChild(col);
  });
  
  // Update AI status badge
  aiStatusBadge.textContent = 'AI: Simulated';
  aiStatusBadge.className = 'ai-status ai-active';
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', initGame);