# 🎮 FOSS MEC — Git Workshop Arena (Day 2)

An interactive, live-networked tournament and learning suite built specifically for **Day 2 of the Git Workshop at Govt. Model Engineering College (FOSS MEC)**.

Runs seamlessly as a **Public Website** or **Local Network Hub** for **~65 participant laptops/phones** and the **workshop organizer's projector** with **pure Python 3 standard library** (zero `pip install`, zero external dependencies).

---

## ⚡ What's New in this Version

* 🌐 **Public Website Access (No Common Wi-Fi Needed)**: Participants can join from anywhere using their personal mobile data (4G/5G) or college network! Deploy free in 1 click to Render/Railway, or launch a zero-signup tunnel from your laptop.
* 🖥️ **Web-Based Organizer Console (`/organizer.html`)**: Manage the entire workshop from your browser with passcode protection (`FOSSMEC2026`). Unlock stages, track first-finishers, and project a fullscreen live leaderboard.
* 🔓 **Instant Stage Unlocking**: When the organizer unlocks Stage 2 (*Git Detective*), all connected participant screens unlock within 2 seconds with an audio chime!
* 🔰 **FOSS MEC Logo & Branding**: Official FOSS MEC emblem integrated into the HUD, welcome screen, and projector display.
* 📚 **35+ Fact-Checked Questions with Variety**: Deep coverage of **branching, fast-forward vs 3-way merging, merge conflicts (`<<<<<<< HEAD`), Pull Requests, undoing (`git restore`, `git stash`), and remotes**.
* 🎲 **Participant Question Randomization**: Each student receives a unique, randomized subset of questions and detective cases to prevent screen peeking and ensure comprehensive learning.
* ⏱️ **Timer & First-Finisher Bonus (+100 Pts)**: Each game tracks completion time. The first student across the room to finish any stage wins an extra +100 Speed Demon Bonus!
* 🎯 **Authentic Stop-on-Bingo**: Unique 3x3 cards per player. The moment a student gets 3 in a row, column, or diagonal, their Bingo round concludes immediately!

---

## 🚀 How to Run as a Public Website (No Common Wi-Fi Needed)

Because venue Wi-Fi may be unavailable or segregated, here are the two easiest ways to host the workshop so all participants can join seamlessly from their mobile data:

### Method 1: Free 1-Click Cloud Deployment (Render.com) — *Recommended*

Deploy once to Render (100% free, no credit card required for standard tier):

1. **Push this repo to your GitHub account**:
   ```bash
   git push origin main
   ```
2. Go to **[Render.com](https://render.com)**, sign in with GitHub, and click **New +** → **Web Service**.
3. Select your `git-workshop-day2` repository.
4. Fill in the basic settings (Render detects Python automatically):
   * **Runtime**: `Python 3`
   * **Build Command**: `echo "Workshop ready"` (or leave blank)
   * **Start Command**: `python3 organizer.py --server-only`
5. Click **Create Web Service**.

Render will deploy your site and provide a permanent public link like:
```text
https://foss-mec-git-workshop.onrender.com
```

* **Students open**: `https://foss-mec-git-workshop.onrender.com` (from any phone or laptop data connection).
* **Organizer opens**: `https://foss-mec-git-workshop.onrender.com/organizer.html` (Passcode: `FOSSMEC2026`) to unlock stages and project the live master leaderboard!

---

### Method 2: Instant Public Tunnel from Organizer Laptop (Zero Sign-up)

If you prefer to run the server directly on your laptop using mobile hotspot:

1. Start the hub in your terminal:
   ```bash
   python3 organizer.py
   ```
2. Open a second terminal window and run:
   ```bash
   ssh -R 80:localhost:5000 nokey@localhost.run
   ```
3. Terminal will output a public HTTPS URL (e.g. `https://random-subdomain.lhr.life`).
4. Share that link with participants via projector or WhatsApp/Discord!

---

### Method 3: Local Wi-Fi / Hotspot Mode (If Shared Network is Available)

If you connect all laptops to a common phone hotspot or venue Wi-Fi:

1. Run on the organizer laptop:
   ```bash
   python3 organizer.py
   ```
2. The terminal will display your LAN IP:
   ```text
   ╔════════════════════════════════════════════════════════════════════════════════╗
   ║                  🌐 FOSS MEC WORKSHOP HUB ACTIVE                              ║
   ║  Projector URL:   http://localhost:5000                                        ║
   ║  Student URL:     http://192.168.1.44:5000 (Open on any laptop / phone)       ║
   ╚════════════════════════════════════════════════════════════════════════════════╝
   ```
3. Students open `http://<YOUR_IP>:5000` in their browsers.

---

## ⏰ Day 2 Schedule & Activity Breakdown

| Time | Session | What Participants Do | Stage Status |
| :--- | :--- | :--- | :---: |
| **3:30–3:45** | **Git Bingo (Laptop Edition)** | Match concepts on a randomized 3x3 card. **First line wins immediately!** | **UNLOCKED** |
| **3:45–4:10** | **Git Detective** | Diagnose real terminal scenes (merge conflicts, detached HEAD, unstaged files). | **🔒 LOCKED** *(Organizer unlocks)* |
| **4:10–4:40** | **Branching & Merging** | Follow along with the facilitator's live demonstration of branching, committing, pushing, and Pull Requests. | **🔒 LOCKED** *(Organizer unlocks)* |
| **4:40–5:10** | **Git Quest (100-Pt Challenge)** | Automated inspection engine that tests your actual local practice repository and grades all 7 tasks. | **🔒 LOCKED** *(Organizer unlocks)* |
| **5:10–5:30** | **Final Showdown & Wrap-Up** | 10 rapid-fire questions randomized from the 35-question bank. | **🔒 LOCKED** *(Organizer unlocks)* |

---

## 📁 Repository Structure

```text
git-workshop-day2/
├── README.md               # Workshop guide and setup instructions
├── play.sh                 # One-click launcher for macOS / Linux
├── play.bat                # One-click launcher for Windows
├── game.py                 # Participant launcher (Web & CLI modes)
├── organizer.py            # Organizer dashboard & Hub server controller
├── web/                    # Built-in Game Interface
│   ├── logo.jpg            # FOSS MEC Official Emblem
│   ├── index.html          # Registration, HUD, Cards, Modals, Leaderboard
│   ├── style.css           # Retro arcade cyberpunk styling with FOSS MEC accents
│   └── game.js             # Live network sync, Web Audio API sound synthesizer
└── engine/                 # Core game engines (Standard Library only)
    ├── __init__.py
    ├── server.py           # Central Workshop Hub server & REST API
    ├── state.py            # Player profiles, stage locks & live leaderboard sync
    ├── ui.py               # Cross-platform ANSI terminal styling & boxes
    ├── bingo.py            # Activity A: 3x3 Git Bingo engine
    ├── detective.py        # Activity B: Git Detective crime scene cases (12 cases)
    ├── branching_guide.py  # Activity C: Interactive branching companion
    ├── quest.py            # Activity D: Real-time 100-pt repo grader & token issuer
    ├── showdown.py         # Activity E: Rapid-fire review quiz & streaks
    └── content/            # Fact-checked question & scenario JSON data
        ├── questions_bank.json    # 35 fact-checked questions across all topics
        ├── detective_cases.json   # 12 real-world terminal crime scenes
        └── bingo_data.json        # 18 commands for unique 3x3 Bingo cards
```
