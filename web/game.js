/* ==========================================================================
   Git Workshop Day 2: Terminal Games Suite - Frontend Engine
   Vanilla JS (No external libraries or CDNs)
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
    [523.25, 659.25, 783.99, 1046.5].forEach((freq, idx) => {
      this.playTone(freq, 'triangle', 0.2, idx * 0.1);
    });
  }
};

let currentProfile = { name: '', class_name: '', score: 0, unlocked_stages: [1] };
let targetUnlockStage = 2;
let bingoData = [];
let bingoGrid = [];
let bingoClueIndex = 0;
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

// --------------------------------------------------------------------------
// Profile & Initialization
// --------------------------------------------------------------------------
async function initProfile() {
  try {
    const res = await fetch('/api/profile');
    const data = await res.json();
    currentProfile = data;
    
    if (data.name && data.class_name) {
      document.getElementById('welcomeOverlay').style.display = 'none';
      updateHud();
    } else {
      document.getElementById('welcomeOverlay').style.display = 'flex';
    }
    updateMissionsUI(data.unlocked_stages || [1]);
  } catch (err) {
    console.error('Failed to load profile:', err);
  }
}

function updateHud() {
  document.getElementById('hudName').textContent = currentProfile.name || 'Guest';
  document.getElementById('hudClass').textContent = currentProfile.class_name || '--';
  document.getElementById('hudScore').textContent = currentProfile.score || 0;
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

      try {
        const res = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, class_name: className })
        });
        const data = await res.json();
        currentProfile = data;
        document.getElementById('welcomeOverlay').style.display = 'none';
        updateHud();
        fetchLeaderboard();
      } catch (err) {
        alert('Error saving registration.');
      }
    });
  }
}

// --------------------------------------------------------------------------
// Stage Unlocking & Polling
// --------------------------------------------------------------------------
function updateMissionsUI(unlockedList) {
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
    // Open passcode unlock modal
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
    msgEl.textContent = 'Error connecting to server.';
  }
}

function startPolling() {
  fetchLeaderboard();
  setInterval(async () => {
    try {
      // Check stage lock updates from organizer
      const statusRes = await fetch('/api/status');
      const statusData = await statusRes.json();
      if (statusData.unlocked) {
        currentProfile.unlocked_stages = statusData.unlocked;
        updateMissionsUI(statusData.unlocked);
      }
      // Update leaderboard
      fetchLeaderboard();
    } catch (e) {}
  }, 3000);
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
      const isCurrent = (item.name === currentProfile.name && item.class_name === currentProfile.class_name);
      if (isCurrent) foundUserRank = index + 1;

      const li = document.createElement('li');
      li.className = `leaderboard-item ${isCurrent ? 'current-user' : ''}`;
      
      let rankBadge = `#${index + 1}`;
      if (index === 0) rankBadge = '🥇';
      else if (index === 1) rankBadge = '🥈';
      else if (index === 2) rankBadge = '🥉';

      li.innerHTML = `
        <span class="leaderboard-rank">${rankBadge}</span>
        <div class="leaderboard-user">
          <span class="leaderboard-name">${escapeHtml(item.name)}</span>
          <span class="leaderboard-class">${escapeHtml(item.class_name)}</span>
        </div>
        <span class="leaderboard-score">${item.score} pts</span>
      `;
      listEl.appendChild(li);
    });

    document.getElementById('hudRank').textContent = foundUserRank !== '-' ? `#${foundUserRank}` : '#-';
  } catch (e) {}
}

async function addPoints(stageNum, points) {
  try {
    const res = await fetch('/api/score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stage: stageNum, points })
    });
    const data = await res.json();
    currentProfile.score = data.score;
    updateHud();
    fetchLeaderboard();
  } catch (e) {}
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = 'none';
}

function escapeHtml(str) {
  return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// --------------------------------------------------------------------------
// 🎯 Activity 1: Git Bingo Game
// --------------------------------------------------------------------------
async function openBingo() {
  AudioFX.init();
  const res = await fetch('/api/bingo/items');
  const allItems = await res.json();
  
  // Pick 9 items randomly for 3x3 board
  const shuffled = [...allItems].sort(() => 0.5 - Math.random());
  bingoGrid = shuffled.slice(0, 9).map(item => ({ ...item, marked: false }));
  bingoData = [...bingoGrid].sort(() => 0.5 - Math.random());
  bingoClueIndex = 0;

  renderBingoBoard();
  showCurrentBingoClue();
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
  if (bingoClueIndex >= bingoData.length) {
    document.getElementById('bingoClueText').textContent = '🎉 All clues completed! Great job on Git Bingo!';
    return;
  }
  const current = bingoData[bingoClueIndex];
  document.getElementById('bingoClueText').textContent = `[Clue ${bingoClueIndex + 1}/${bingoData.length}]: ${current.prompt}`;
}

function onBingoCellClick(idx) {
  if (bingoClueIndex >= bingoData.length) return;
  const targetItem = bingoData[bingoClueIndex];
  const clicked = bingoGrid[idx];
  const feedbackEl = document.getElementById('bingoFeedback');

  if (clicked.command === targetItem.command) {
    if (!clicked.marked) {
      clicked.marked = true;
      AudioFX.success();
      addPoints(1, 20);
      feedbackEl.innerHTML = `<span style="color:#39d353; font-weight:bold;">✔ CORRECT!</span> Marked square '${clicked.command}' (+20 pts).<br><small style="color:#8b949e;">${targetItem.explanation}</small>`;
      checkBingoWin();
    }
    bingoClueIndex++;
    renderBingoBoard();
    setTimeout(showCurrentBingoClue, 1200);
  } else {
    AudioFX.error();
    feedbackEl.innerHTML = `<span style="color:#f85149; font-weight:bold;">✘ NOT QUITE!</span> You clicked '${clicked.command}'. Look for '${targetItem.command}'.`;
  }
}

function checkBingoWin() {
  const lines = [
    [0,1,2], [3,4,5], [6,7,8], // Rows
    [0,3,6], [1,4,7], [2,5,8], // Columns
    [0,4,8], [2,4,6]           // Diagonals
  ];
  for (let line of lines) {
    if (line.every(i => bingoGrid[i].marked)) {
      if (!bingoGrid._bingoAwarded) {
        bingoGrid._bingoAwarded = true;
        AudioFX.bingo();
        addPoints(1, 50);
        alert('🎉🎉🎉 BINGO! You connected 3 in a line! (+50 BONUS POINTS) 🎉🎉🎉');
      }
      break;
    }
  }
}

// --------------------------------------------------------------------------
// 🕵️ Activity 2: Git Detective Game
// --------------------------------------------------------------------------
async function openDetective() {
  AudioFX.init();
  const res = await fetch('/api/detective/cases');
  detectiveCases = await res.json();
  detectiveCaseIndex = 0;
  loadDetectiveCase();
  document.getElementById('detectiveModal').style.display = 'flex';
}

function loadDetectiveCase() {
  if (detectiveCaseIndex >= detectiveCases.length) {
    document.getElementById('detectiveTitle').textContent = '🕵️ ALL CASES SOLVED!';
    document.getElementById('detectiveScenario').textContent = 'Congratulations! You solved every crime scene case!';
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
    addPoints(2, 20);
    fb.innerHTML = `
      <div style="background: rgba(46,160,67,0.15); border: 1px solid #39d353; padding: 12px; border-radius: 6px;">
        <span style="color:#39d353; font-weight:bold;">✔ CASE SOLVED! (+20 Points)</span><br>
        <p style="margin-top:6px; font-size:0.9rem;">${escapeHtml(c.explanation)}</p>
        <button class="btn-play" style="margin-top:10px;" onclick="nextDetectiveCase()">NEXT CASE ➔</button>
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
  AudioFX.success();
  addPoints(3, 20);
  alert('Workflow Completed! 20 points awarded.');
  closeModal('branchingModal');
}

// --------------------------------------------------------------------------
// ⚔️ Activity 4: Git Quest Live Grader
// --------------------------------------------------------------------------
function openQuest() {
  AudioFX.init();
  document.getElementById('questResultsArea').innerHTML = '';
  document.getElementById('questModal').style.display = 'flex';
}

async function runQuestVerification() {
  const repoPath = document.getElementById('questRepoPath').value.trim();
  const resArea = document.getElementById('questResultsArea');
  resArea.innerHTML = '<p style="color:var(--accent-yellow);">🔍 Inspecting local Git repository...</p>';

  try {
    const res = await fetch('/api/quest/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_path: repoPath })
    });
    const data = await res.json();
    
    let html = `
      <div style="margin-top:16px; background:var(--bg-card); padding:16px; border-radius:8px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h4 style="color:#fff;">SCORECARD: ${data.total_score} / 100 POINTS</h4>
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
      addPoints(4, data.total_score);
    }
  } catch (err) {
    resArea.innerHTML = '<p style="color:#f85149;">Failed to inspect repository. Make sure the folder path is correct.</p>';
  }
}

// --------------------------------------------------------------------------
// ⚡ Activity 5: Final Showdown
// --------------------------------------------------------------------------
async function openShowdown() {
  AudioFX.init();
  const res = await fetch('/api/showdown/questions');
  showdownQuestions = await res.json();
  showdownIndex = 0;
  showdownScore = 0;
  loadShowdownQuestion();
  document.getElementById('showdownModal').style.display = 'flex';
}

function loadShowdownQuestion() {
  if (showdownIndex >= showdownQuestions.length) {
    document.getElementById('showdownHeader').textContent = '⚡ SHOWDOWN COMPLETE!';
    document.getElementById('showdownArea').innerHTML = `
      <div style="text-align:center; padding:20px;">
        <h2 style="color:#39d353;">Final Quiz Complete!</h2>
        <p style="margin:12px 0; font-size:1.1rem;">You scored ${showdownScore} points in the Grand Finale!</p>
        <button class="btn-primary" onclick="closeModal('showdownModal')">WRAP UP 🏆</button>
      </div>
    `;
    return;
  }

  const q = showdownQuestions[showdownIndex];
  document.getElementById('showdownHeader').textContent = `⚡ FINAL SHOWDOWN: QUESTION ${showdownIndex + 1}/${showdownQuestions.length}`;
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
    addPoints(5, 10);
    fb.innerHTML = `
      <div style="color:#39d353; font-weight:bold; margin-bottom:10px;">✔ CORRECT! (+10 pts)</div>
      <button class="btn-play" onclick="nextShowdownQuestion()">NEXT QUESTION ➔</button>
    `;
  } else {
    AudioFX.error();
    fb.innerHTML = `
      <div style="color:#f85149; font-weight:bold; margin-bottom:10px;">✘ INCORRECT. Correct answer: ${escapeHtml(q.options[q.correct_index])}</div>
      <button class="btn-play" onclick="nextShowdownQuestion()">CONTINUE ➔</button>
    `;
  }
}

function nextShowdownQuestion() {
  showdownIndex++;
  loadShowdownQuestion();
}
