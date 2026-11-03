/* ==========================================================================
   FOSS MEC — Git Workshop Day 2: Terminal Games Suite
   Frontend Engine with Live Network Sync & Real-time Room Leaderboard
   ========================================================================== */

// Web Audio API Synthesizer (Zero sound files needed!)
const AudioFX = {
  ctx: null,
  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) this.ctx = new AudioContext();
    }
  },
  playTone(freq, type, duration, delay = 0) {
    if (!this.ctx) this.init();
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime + delay);
      gain.gain.setValueAtTime(0.15, this.ctx.currentTime + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + delay + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(this.ctx.currentTime + delay);
      osc.stop(this.ctx.currentTime + delay + duration);
    } catch (e) {}
  },
  success() {
    this.playTone(523.25, 'sine', 0.1, 0);       // C5
    this.playTone(659.25, 'sine', 0.15, 0.08);   // E5
    this.playTone(783.99, 'sine', 0.25, 0.16);   // G5
  },
  error() {
    this.playTone(220, 'sawtooth', 0.2, 0);
    this.playTone(180, 'sawtooth', 0.25, 0.1);
  },
  bingo() {
    [523.25, 659.25, 783.99, 1046.5, 1318.5].forEach((freq, idx) => {
      this.playTone(freq, 'triangle', 0.25, idx * 0.1);
    });
  },
  stageUnlocked() {
    [440, 554.37, 659.25, 880].forEach((freq, idx) => {
      this.playTone(freq, 'sine', 0.2, idx * 0.09);
    });
  },
  firstPlace() {
    [587.33, 739.99, 880.0, 1174.66].forEach((freq, idx) => {
      this.playTone(freq, 'square', 0.3, idx * 0.12);
    });
  }
};

let currentProfile = {
  name: localStorage.getItem('foss_player_name') || '',
  class_name: localStorage.getItem('foss_player_class') || '',
  score: 0,
  total_time: 0.0,
  formatted_time: '00:00',
  unlocked_stages: [1]
};

let targetUnlockStage = 2;
let activeGameStartTime = null;
let activeGameTimerInterval = null;

// Game state variables
let bingoPool = [];
let bingoGrid = [];
let bingoClueIndex = 0;
let bingoOver = false;

let detectiveCases = [];
let detectiveCaseIndex = 0;

let showdownQuestions = [];
let showdownIndex = 0;
let showdownScore = 0;

document.addEventListener('DOMContentLoaded', () => {
  initProfile();
  setupEventListeners();
  startPolling();
});

function formatSeconds(secs) {
  const s = Math.round(Number(secs) || 0);
  const m = Math.floor(s / 60);
  const remainingSecs = s % 60;
  return `${String(m).padStart(2, '0')}:${String(remainingSecs).padStart(2, '0')}`;
}

function startRoundTimer(displayElId) {
  if (activeGameTimerInterval) clearInterval(activeGameTimerInterval);
  activeGameStartTime = Date.now();
  const el = document.getElementById(displayElId);
  if (el) el.textContent = '00:00';

  activeGameTimerInterval = setInterval(() => {
    const elapsedSecs = (Date.now() - activeGameStartTime) / 1000;
    if (el) el.textContent = formatSeconds(elapsedSecs);
  }, 500);
}

function stopRoundTimer() {
  if (activeGameTimerInterval) {
    clearInterval(activeGameTimerInterval);
    activeGameTimerInterval = null;
  }
  if (!activeGameStartTime) return 0.0;
  const elapsed = (Date.now() - activeGameStartTime) / 1000;
  activeGameStartTime = null;
  return Math.round(elapsed * 10) / 10;
}

// --------------------------------------------------------------------------
// Profile & Initialization
// --------------------------------------------------------------------------
async function initProfile() {
  if (currentProfile.name && currentProfile.class_name) {
    document.getElementById('welcomeOverlay').style.display = 'none';
    updateHud();
    // Re-register on hub
    try {
      await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: currentProfile.name,
          class_name: currentProfile.class_name
        })
      });
    } catch (e) {}
  } else {
    document.getElementById('welcomeOverlay').style.display = 'flex';
  }

  // Fetch initial status
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (data.unlocked) {
      currentProfile.unlocked_stages = data.unlocked;
      updateMissionsUI(data.unlocked);
    }
  } catch (e) {}
}

function updateHud() {
  document.getElementById('hudName').textContent = currentProfile.name || 'Guest';
  document.getElementById('hudClass').textContent = currentProfile.class_name || '--';
  document.getElementById('hudScore').textContent = currentProfile.score || 0;
  document.getElementById('hudTime').textContent = currentProfile.formatted_time || '00:00';
}

function setupEventListeners() {
  const form = document.getElementById('registerForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      AudioFX.init();
      AudioFX.success();
      const name = document.getElementById('playerName').value.trim();
      const className = document.getElementById('playerClass').value.trim();
      if (!name || !className) return;

      currentProfile.name = name;
      currentProfile.class_name = className;
      localStorage.setItem('foss_player_name', name);
      localStorage.setItem('foss_player_class', className);

      try {
        const res = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, class_name: className })
        });
        const data = await res.json();
        document.getElementById('welcomeOverlay').style.display = 'none';
        updateHud();
        fetchLeaderboard();
      } catch (err) {
        alert('Error connecting to workshop hub.');
      }
    });
  }
}

// --------------------------------------------------------------------------
// Stage Unlocking & Live Polling
// --------------------------------------------------------------------------
let previousUnlockedCount = 1;

function updateMissionsUI(unlockedList) {
  // Check if a new stage was unlocked by organizer!
  if (unlockedList.length > previousUnlockedCount) {
    previousUnlockedCount = unlockedList.length;
    AudioFX.stageUnlocked();
  }

  for (let stage = 1; stage <= 5; stage++) {
    const card = document.getElementById(`cardStage${stage}`);
    const action = document.getElementById(`actionStage${stage}`);
    if (!card) continue;

    const isUnlocked = unlockedList.includes(stage);
    if (isUnlocked) {
      card.classList.remove('locked');
      card.classList.add('unlocked');
      if (action) {
        action.innerHTML = '<button class="btn-play">PLAY NOW</button>';
      }
    } else {
      card.classList.remove('unlocked');
      card.classList.add('locked');
      if (action) {
        action.innerHTML = '<span class="locked-tag">🔒 LOCKED</span>';
      }
    }
  }
}

function handleStageClick(stageNum, launchFunc) {
  AudioFX.init();
  if (currentProfile.unlocked_stages && currentProfile.unlocked_stages.includes(stageNum)) {
    launchFunc();
  } else {
    targetUnlockStage = stageNum;
    document.getElementById('unlockModalTitle').textContent = `🔒 STAGE ${stageNum} LOCKED`;
    document.getElementById('unlockPasscode').value = '';
    document.getElementById('unlockMsg').textContent = '';
    document.getElementById('unlockModal').style.display = 'flex';
  }
}

async function submitPasscode() {
  const code = document.getElementById('unlockPasscode').value.trim();
  const msgEl = document.getElementById('unlockMsg');
  if (!code) return;

  try {
    const res = await fetch('/api/unlock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stage: targetUnlockStage, password: code })
    });
    const result = await res.json();
    if (result.success) {
      AudioFX.success();
      msgEl.style.color = '#39d353';
      msgEl.textContent = '✔ ' + result.message;
      if (!currentProfile.unlocked_stages.includes(targetUnlockStage)) {
        currentProfile.unlocked_stages.push(targetUnlockStage);
      }
      updateMissionsUI(currentProfile.unlocked_stages);
      setTimeout(() => closeModal('unlockModal'), 1000);
    } else {
      AudioFX.error();
      msgEl.style.color = '#f85149';
      msgEl.textContent = '✘ ' + result.message;
    }
  } catch (err) {
    msgEl.textContent = 'Error connecting to hub.';
  }
}

function startPolling() {
  fetchLeaderboard();
  setInterval(async () => {
    try {
      // 1. Check stage status from organizer
      const statusRes = await fetch('/api/status');
      const statusData = await statusRes.json();
      if (statusData.unlocked) {
        currentProfile.unlocked_stages = statusData.unlocked;
        updateMissionsUI(statusData.unlocked);
      }
      // 2. Refresh room leaderboard
      fetchLeaderboard();
    } catch (e) {}
  }, 2000);
}

async function fetchLeaderboard() {
  try {
    const res = await fetch('/api/leaderboard');
    const list = await res.json();
    const listEl = document.getElementById('leaderboardList');
    if (!listEl) return;

    listEl.innerHTML = '';
    let foundUserRank = '-';

    list.forEach((item, index) => {
      const isCurrent = (item.name.toLowerCase() === currentProfile.name.toLowerCase() &&
                         item.class_name.toLowerCase() === currentProfile.class_name.toLowerCase());
      if (isCurrent) {
        foundUserRank = index + 1;
        currentProfile.score = item.score;
        currentProfile.total_time = item.total_time;
        currentProfile.formatted_time = item.formatted_time || formatSeconds(item.total_time);
        updateHud();
      }

      const li = document.createElement('li');
      li.className = `leaderboard-item ${isCurrent ? 'current-user' : ''}`;
      
      let rankBadge = `#${index + 1}`;
      if (index === 0) rankBadge = '🥇';
      else if (index === 1) rankBadge = '🥈';
      else if (index === 2) rankBadge = '🥉';

      const timeDisplay = item.formatted_time || formatSeconds(item.total_time);

      li.innerHTML = `
        <span class="leaderboard-rank">${rankBadge}</span>
        <div class="leaderboard-user">
          <span class="leaderboard-name">${escapeHtml(item.name)}</span>
          <span class="leaderboard-class">${escapeHtml(item.class_name)} • ⏱️ ${timeDisplay}</span>
        </div>
        <span class="leaderboard-score">${item.score} pts</span>
      `;
      listEl.appendChild(li);
    });

    document.getElementById('hudRank').textContent = foundUserRank !== '-' ? `#${foundUserRank}` : '#-';
  } catch (e) {}
}

async function addPoints(stageNum, points, timeTaken = 0.0, isCompletion = false) {
  try {
    const res = await fetch('/api/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: currentProfile.name,
        class_name: currentProfile.class_name,
        stage: stageNum,
        points: points,
        time_taken: timeTaken,
        is_completion: isCompletion
      })
    });
    const data = await res.json();
    currentProfile.score = data.score;
    currentProfile.total_time = data.total_time;
    currentProfile.formatted_time = data.formatted_time;
    updateHud();
    fetchLeaderboard();

    if (data.is_first && data.bonus_pts > 0) {
      AudioFX.firstPlace();
      showFirstPlaceCelebration(stageNum, data.bonus_pts);
    }
  } catch (e) {}
}

function showFirstPlaceCelebration(stageNum, bonusPts) {
  alert(`⚡⚡⚡ FIRST FINISHER SPEED BONUS! ⚡⚡⚡\nYou were the FIRST person across the room to complete Stage ${stageNum}!\n+${bonusPts} BONUS POINTS awarded!`);
}

function closeModal(modalId) {
  stopRoundTimer();
  document.getElementById(modalId).style.display = 'none';
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// --------------------------------------------------------------------------
// 🎯 Activity 1: Git Bingo Game (STOP ON BINGO + UNIQUE 3x3 CARDS)
// --------------------------------------------------------------------------
async function openBingo() {
  AudioFX.init();
  const res = await fetch('/api/bingo/items');
  const allItems = await res.json();
  
  bingoOver = false;
  // Unique random 3x3 card sampled for this player
  const shuffledCard = [...allItems].sort(() => 0.5 - Math.random()).slice(0, 9);
  bingoGrid = shuffledCard.map(item => ({ ...item, marked: false }));
  
  // Clues are called from the master pool in randomized order
  bingoPool = [...allItems].sort(() => 0.5 - Math.random());
  bingoClueIndex = 0;

  renderBingoBoard();
  showCurrentBingoClue();
  startRoundTimer('bingoTimerDisplay');
  document.getElementById('bingoModal').style.display = 'flex';
}

function renderBingoBoard() {
  const gridEl = document.getElementById('bingoGrid');
  gridEl.innerHTML = '';

  bingoGrid.forEach((cell, idx) => {
    const div = document.createElement('div');
    div.className = `bingo-cell ${cell.marked ? 'marked' : ''}`;
    div.textContent = cell.command;
    div.onclick = () => onBingoCellClick(idx);
    gridEl.appendChild(div);
  });
}

function showCurrentBingoClue() {
  if (bingoOver) return;

  if (bingoClueIndex >= bingoPool.length) {
    const elapsed = stopRoundTimer();
    document.getElementById('bingoClueText').textContent = 'All clues called! Bingo round finished.';
    addPoints(1, 0, elapsed, true);
    return;
  }

  const current = bingoPool[bingoClueIndex];
  document.getElementById('bingoClueText').textContent = `[Call #${bingoClueIndex + 1} of ${bingoPool.length}]: ${current.prompt}`;
}

function onBingoCellClick(idx) {
  if (bingoOver || bingoClueIndex >= bingoPool.length) return;
  const currentClue = bingoPool[bingoClueIndex];
  const clicked = bingoGrid[idx];
  const feedbackEl = document.getElementById('bingoFeedback');

  if (clicked.command === currentClue.command) {
    if (!clicked.marked) {
      clicked.marked = true;
      AudioFX.success();
      feedbackEl.innerHTML = `<span style="color:#39d353; font-weight:bold;">✔ CORRECT!</span> Marked square '${clicked.command}' (+20 pts).`;
      
      // Check for BINGO! If 3 in a line, STOP IMMEDIATELY!
      const hasBingo = checkBingoWin();
      if (hasBingo) {
        bingoOver = true;
        const elapsed = stopRoundTimer();
        AudioFX.bingo();
        
        // Award points + Bingo 50 pts + completion flag (checks first finisher bonus)
        addPoints(1, 70, elapsed, true);
        
        renderBingoBoard();
        feedbackEl.innerHTML = `
          <div style="background: rgba(46,160,67,0.25); border: 2px solid #39d353; padding: 16px; border-radius: 8px; text-align: center; margin-top: 10px;">
            <h2 style="color: #39d353; margin-bottom: 6px;">🎉🎉🎉 BINGO ACHIEVED! 🎉🎉🎉</h2>
            <p style="font-size: 1.1rem; color: #fff;">You completed 3 in a line in <strong>${formatSeconds(elapsed)} (${elapsed}s)</strong>!</p>
            <p style="color: #bc8cff; font-weight: bold; margin-top: 4px;">Game stops immediately! Points & time submitted to live room leaderboard.</p>
            <button class="btn-primary" style="margin-top: 12px; max-width: 200px;" onclick="closeModal('bingoModal')">COLLECT & RETURN 🏆</button>
          </div>
        `;
        document.getElementById('bingoClueText').textContent = '🎉 BINGO COMPLETED! You won!';
        return;
      } else {
        addPoints(1, 20, 0, false);
      }
    }
    renderBingoBoard();
    bingoClueIndex++;
    setTimeout(showCurrentBingoClue, 1000);
  } else {
    AudioFX.error();
    feedbackEl.innerHTML = `<span style="color:#f85149; font-weight:bold;">✘ NOT QUITE!</span> You clicked '${clicked.command}'. Look for '${currentClue.command}'.`;
  }
}

function skipBingoClue() {
  if (bingoOver) return;
  const currentClue = bingoPool[bingoClueIndex];
  const feedbackEl = document.getElementById('bingoFeedback');
  feedbackEl.innerHTML = `<span style="color:#8b949e;">Clue skipped ('${currentClue.command}' was not marked). Next clue called...</span>`;
  bingoClueIndex++;
  showCurrentBingoClue();
}

function checkBingoWin() {
  const lines = [
    [0,1,2], [3,4,5], [6,7,8], // Rows
    [0,3,6], [1,4,7], [2,5,8], // Columns
    [0,4,8], [2,4,6]           // Diagonals
  ];
  return lines.some(line => line.every(i => bingoGrid[i].marked));
}

// --------------------------------------------------------------------------
// 🕵️ Activity 2: Git Detective Game (RANDOMIZED CASES)
// --------------------------------------------------------------------------
async function openDetective() {
  AudioFX.init();
  // Fetch random 6 cases from 12-case pool
  const res = await fetch('/api/detective/cases?count=6');
  detectiveCases = await res.json();
  detectiveCaseIndex = 0;
  loadDetectiveCase();
  startRoundTimer('detectiveTimerDisplay');
  document.getElementById('detectiveModal').style.display = 'flex';
}

function loadDetectiveCase() {
  if (detectiveCaseIndex >= detectiveCases.length) {
    const elapsed = stopRoundTimer();
    addPoints(2, 0, elapsed, true);
    document.getElementById('detectiveTitle').textContent = '🕵️ ALL CASES SOLVED!';
    document.getElementById('detectiveScenario').textContent = `You solved all cases in ${formatSeconds(elapsed)}!`;
    document.getElementById('detectiveTerminal').innerHTML = '<span class="cmd">Investigation Complete: 100% Case Clearance Rate!</span>';
    document.getElementById('detectiveOptions').innerHTML = '';
    return;
  }

  const c = detectiveCases[detectiveCaseIndex];
  document.getElementById('detectiveTitle').textContent = `🕵️ CASE ${detectiveCaseIndex + 1}/${detectiveCases.length}: ${c.title.toUpperCase()}`;
  document.getElementById('detectiveScenario').textContent = c.scenario;
  document.getElementById('detectiveTerminal').innerHTML = `<span class="cmd">$ ${escapeHtml(c.command_sim)}</span>\n${escapeHtml(c.output_sim)}`;
  document.getElementById('detectiveQuestion').textContent = c.question;
  document.getElementById('detectiveFeedback').innerHTML = '';

  const optsEl = document.getElementById('detectiveOptions');
  optsEl.innerHTML = '';
  c.options.forEach((opt, idx) => {
    const item = document.createElement('div');
    item.className = 'option-item';
    item.innerHTML = `<span class="option-num">[${idx + 1}]</span> <span>${escapeHtml(opt)}</span>`;
    item.onclick = () => selectDetectiveOption(idx);
    optsEl.appendChild(item);
  });
}

function selectDetectiveOption(selectedIdx) {
  const c = detectiveCases[detectiveCaseIndex];
  const fb = document.getElementById('detectiveFeedback');
  if (selectedIdx === c.correct_index) {
    AudioFX.success();
    const isLast = (detectiveCaseIndex === detectiveCases.length - 1);
    const elapsed = isLast ? stopRoundTimer() : 0.0;
    addPoints(2, 20, elapsed, isLast);

    fb.innerHTML = `
      <div style="background: rgba(46,160,67,0.15); border: 1px solid #39d353; padding: 12px; border-radius: 6px;">
        <span style="color:#39d353; font-weight:bold;">✔ CASE SOLVED! (+20 Points)</span><br>
        <p style="margin-top:6px; font-size:0.9rem;">${escapeHtml(c.explanation)}</p>
        <button class="btn-play" style="margin-top:10px;" onclick="nextDetectiveCase()">${isLast ? 'FINISH INVESTIGATION ➔' : 'NEXT CASE ➔'}</button>
      </div>
    `;
  } else {
    AudioFX.error();
    fb.innerHTML = `
      <div style="background: rgba(248,81,73,0.15); border: 1px solid #f85149; padding: 12px; border-radius: 6px;">
        <span style="color:#f85149; font-weight:bold;">✘ INCORRECT DIAGNOSIS!</span> Try another option.
      </div>
    `;
  }
}

function nextDetectiveCase() {
  detectiveCaseIndex++;
  loadDetectiveCase();
}

// --------------------------------------------------------------------------
// 🌿 Activity 3: Branching Walkthrough
// --------------------------------------------------------------------------
function openBranching() {
  AudioFX.init();
  startRoundTimer('branchingTimerDisplay');
  const container = document.getElementById('branchingStepsContainer');
  container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:14px;">
      <div style="background:var(--bg-card); padding:16px; border-radius:8px; border-left:4px solid #00f0ff;">
        <h4 style="color:#00f0ff;">Step 1: Create & Switch to Branch</h4>
        <code style="display:block; background:#000; padding:8px; margin:8px 0; border-radius:4px; color:#7ee787;">git switch -c add-my-section</code>
        <small style="color:#8b949e;">Isolates your feature work away from the main branch.</small>
      </div>
      <div style="background:var(--bg-card); padding:16px; border-radius:8px; border-left:4px solid #00f0ff;">
        <h4 style="color:#00f0ff;">Step 2: Edit README.md</h4>
        <code style="display:block; background:#000; padding:8px; margin:8px 0; border-radius:4px; color:#7ee787;">echo "## Contributed by My Name" >> README.md</code>
        <small style="color:#8b949e;">Make changes in your editor, then check with 'git status'.</small>
      </div>
      <div style="background:var(--bg-card); padding:16px; border-radius:8px; border-left:4px solid #00f0ff;">
        <h4 style="color:#00f0ff;">Step 3: Stage and Commit</h4>
        <code style="display:block; background:#000; padding:8px; margin:8px 0; border-radius:4px; color:#7ee787;">git add . && git commit -m "Add my section"</code>
        <small style="color:#8b949e;">Saves a snapshot on your new branch.</small>
      </div>
      <div style="background:var(--bg-card); padding:16px; border-radius:8px; border-left:4px solid #00f0ff;">
        <h4 style="color:#00f0ff;">Step 4: Push Upstream</h4>
        <code style="display:block; background:#000; padding:8px; margin:8px 0; border-radius:4px; color:#7ee787;">git push -u origin add-my-section</code>
        <small style="color:#8b949e;">Uploads your branch to GitHub.</small>
      </div>
      <div style="background:var(--bg-card); padding:16px; border-radius:8px; border-left:4px solid #00f0ff;">
        <h4 style="color:#00f0ff;">Step 5 & 6: Pull Request & Merge</h4>
        <small style="color:#8b949e;">Open GitHub in your browser, click 'Compare & pull request', review the changes, and click 'Merge'!</small>
      </div>
      <button class="btn-primary" onclick="claimBranchingPoints()">COMPLETE WORKFLOW (+20 PTS) ✔</button>
    </div>
  `;
  document.getElementById('branchingModal').style.display = 'flex';
}

function claimBranchingPoints() {
  const elapsed = stopRoundTimer();
  AudioFX.success();
  addPoints(3, 20, elapsed, true);
  alert(`Workflow Completed in ${formatSeconds(elapsed)}! 20 points awarded.`);
  closeModal('branchingModal');
}

// --------------------------------------------------------------------------
// ⚔️ Activity 4: Git Quest Live Grader
// --------------------------------------------------------------------------
function openQuest() {
  AudioFX.init();
  startRoundTimer('questTimerDisplay');
  document.getElementById('questResultsArea').innerHTML = '';
  document.getElementById('questModal').style.display = 'flex';
}

async function runQuestVerification() {
  const repoPath = document.getElementById('questRepoPath') ? document.getElementById('questRepoPath').value.trim() : '';
  const githubUrl = document.getElementById('questGithubUrl') ? document.getElementById('questGithubUrl').value.trim() : '';
  const resArea = document.getElementById('questResultsArea');
  
  if (!repoPath && !githubUrl) {
    alert("Please provide either your GitHub repo/PR link (or local repo folder path) to inspect!");
    return;
  }

  const elapsed = stopRoundTimer();
  resArea.innerHTML = '<p style="color:var(--accent-yellow);">🔍 Inspecting Git repository & verifying workshop challenges...</p>';

  try {
    const res = await fetch('/api/quest/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        repo_path: repoPath,
        github_url: githubUrl,
        name: currentProfile.name,
        time_taken: elapsed
      })
    });
    const data = await res.json();
    
    let html = `
      <div style="margin-top:16px; background:var(--bg-card); padding:16px; border-radius:8px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h4 style="color:#fff;">SCORECARD: ${data.total_score} / 100 POINTS • ⏱️ ${formatSeconds(elapsed)}</h4>
          <span style="background:#238636; color:#fff; padding:4px 10px; border-radius:4px; font-weight:bold;">${data.token}</span>
        </div>
        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
          <tr style="border-bottom:1px solid #30363d; text-align:left; color:#8b949e;">
            <th style="padding:6px;">Task</th>
            <th>Status</th>
            <th>Points</th>
            <th>Details</th>
          </tr>
    `;

    data.results.forEach(r => {
      html += `
        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
          <td style="padding:8px 6px; font-weight:600;">${escapeHtml(r.title)}</td>
          <td style="color:${r.passed ? '#39d353' : '#f85149'}; font-weight:bold;">${r.passed ? '✔ PASS' : '✘ PENDING'}</td>
          <td>${r.awarded}/${r.points}</td>
          <td style="color:#8b949e; font-size:0.85rem;">${escapeHtml(r.details)}</td>
        </tr>
      `;
    });

    html += `</table></div>`;
    resArea.innerHTML = html;

    if (data.total_score > 0) {
      AudioFX.success();
      const isComplete = (data.total_score === 100);
      addPoints(4, data.total_score, elapsed, isComplete);
    }
  } catch (err) {
    resArea.innerHTML = '<p style="color:#f85149;">Failed to inspect repository. Make sure the folder path is correct.</p>';
  }
}

// --------------------------------------------------------------------------
// ⚡ Activity 5: Final Showdown (35+ QUESTION BANK RANDOMIZATION)
// --------------------------------------------------------------------------
async function openShowdown() {
  AudioFX.init();
  // Fetch random 10 questions from the 35+ fact-checked question bank!
  const res = await fetch('/api/showdown/questions?count=10');
  showdownQuestions = await res.json();
  showdownIndex = 0;
  showdownScore = 0;
  loadShowdownQuestion();
  startRoundTimer('showdownTimerDisplay');
  document.getElementById('showdownModal').style.display = 'flex';
}

function loadShowdownQuestion() {
  if (showdownIndex >= showdownQuestions.length) {
    const elapsed = stopRoundTimer();
    addPoints(5, 0, elapsed, true);
    document.getElementById('showdownHeader').textContent = '⚡ SHOWDOWN COMPLETE!';
    document.getElementById('showdownArea').innerHTML = `
      <div style="text-align:center; padding:20px;">
        <h2 style="color:#39d353;">Final Quiz Complete!</h2>
        <p style="margin:12px 0; font-size:1.1rem;">You scored ${showdownScore} points in <strong>${formatSeconds(elapsed)}</strong>!</p>
        <button class="btn-primary" onclick="closeModal('showdownModal')">WRAP UP 🏆</button>
      </div>
    `;
    return;
  }

  const q = showdownQuestions[showdownIndex];
  document.getElementById('showdownHeader').textContent = `⚡ FINAL SHOWDOWN: QUESTION ${showdownIndex + 1}/${showdownQuestions.length} (${q.topic})`;
  document.getElementById('showdownQuestionText').textContent = q.question;
  document.getElementById('showdownFeedback').innerHTML = '';

  const optsEl = document.getElementById('showdownOptions');
  optsEl.innerHTML = '';
  q.options.forEach((opt, idx) => {
    const item = document.createElement('div');
    item.className = 'option-item';
    item.innerHTML = `<span class="option-num">[${idx + 1}]</span> <span>${escapeHtml(opt)}</span>`;
    item.onclick = () => selectShowdownOption(idx);
    optsEl.appendChild(item);
  });
}

function selectShowdownOption(idx) {
  const q = showdownQuestions[showdownIndex];
  const fb = document.getElementById('showdownFeedback');
  if (idx === q.correct_index) {
    AudioFX.success();
    showdownScore += 10;
    const isLast = (showdownIndex === showdownQuestions.length - 1);
    const elapsed = isLast ? stopRoundTimer() : 0.0;
    addPoints(5, 10, elapsed, isLast);

    fb.innerHTML = `
      <div style="color:#39d353; font-weight:bold; margin-bottom:10px;">✔ CORRECT! (+10 pts)<br><small style="color:#8b949e;">${escapeHtml(q.explanation)}</small></div>
      <button class="btn-play" onclick="nextShowdownQuestion()">${isLast ? 'SEE RESULTS ➔' : 'NEXT QUESTION ➔'}</button>
    `;
  } else {
    AudioFX.error();
    const isLast = (showdownIndex === showdownQuestions.length - 1);
    if (isLast) stopRoundTimer();
    fb.innerHTML = `
      <div style="color:#f85149; font-weight:bold; margin-bottom:10px;">✘ INCORRECT. Correct answer: ${escapeHtml(q.options[q.correct_index])}<br><small style="color:#8b949e;">${escapeHtml(q.explanation)}</small></div>
      <button class="btn-play" onclick="nextShowdownQuestion()">${isLast ? 'SEE RESULTS ➔' : 'CONTINUE ➔'}</button>
    `;
  }
}

function nextShowdownQuestion() {
  showdownIndex++;
  loadShowdownQuestion();
}
