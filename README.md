# 🎮 FOSS MEC — Git Workshop Arena (Day 2)

An interactive, live-networked tournament and learning suite built specifically for **Day 2 of the Git Workshop at Govt. Model Engineering College (FOSS MEC)**.

Runs seamlessly across **~65 participant laptops** and the **workshop organizer's projector laptop** with **pure Python 3 standard library** (zero `pip install`, zero external dependencies).

---

## ⚡ What's New in this Version

* 🌐 **Live Room-Wide Leaderboard Sync**: The organizer's laptop runs the Central Workshop Hub. When any student registers or scores points, their name, class, score, and completion time update live on every screen in the room!
* 🔓 **Instant Stage Unlocking**: The organizer unlocks Stage 2 (*Git Detective*) with one click; all connected participant laptops immediately unlock Stage 2 in real time (polling every 2 seconds with audio chime).
* 🔰 **FOSS MEC Logo & Branding**: Official FOSS MEC emblem integrated into the top HUD, welcome screen, and projector display.
* 📚 **35+ Fact-Checked Questions with Variety**: Deep coverage of **branching, merging, merge conflicts (`<<<<<<< HEAD`), Pull Requests, undoing (`git restore`, `git stash`), and remotes**.
* 🎲 **Participant Question Randomization**: Each student receives a unique, randomized subset of questions and detective cases to prevent screen peeking and ensure comprehensive learning.
* ⏱️ **Timer & First-Finisher Bonus (+100 Pts)**: Each game tracks completion time. The first student across the room to finish any stage wins an extra +100 Speed Demon Bonus!
* 🎯 **Authentic Stop-on-Bingo**: Unique 3x3 cards per player. The moment a student gets 3 in a row, column, or diagonal, their Bingo round concludes immediately!

---

## 🚀 Workshop Setup & Running Guide

### 1. For You (The Organizer) — On the Projector Laptop

Connect your laptop to the venue Wi-Fi / Hotspot and projector, open your terminal, and run:

```bash
python3 organizer.py
```

The terminal will display:
```text
╔════════════════════════════════════════════════════════════════════════════════╗
║                  🌐 FOSS MEC WORKSHOP HUB ACTIVE                              ║
║  Projector URL:   http://localhost:5000                                        ║
║  Student URL:     http://192.168.1.44:5000 (Open on any laptop / phone)       ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

* **Projector View**: Open `http://localhost:5000` in your browser (or select `[1]` in the terminal menu) to project the **Live Master Leaderboard** onto the big screen.
* **Stage Controller**: Select `[0] Stage Unlock Controller` in `organizer.py` whenever you are ready to open Stage 2, 3, 4, or 5.

---

### 2. For Participants (~65 Students)

Students can join in **either of two ways**:

#### Option A: Direct Browser (Easiest — No Setup Needed!)
Students connect to the same Wi-Fi / hotspot and simply open the URL shown on your projector:
```text
http://<ORGANIZER_IP>:5000
```
*(Example: `http://192.168.1.44:5000`)*. They can play immediately from Chrome, Firefox, Safari, or Edge!

#### Option B: Terminal / Local Clone
If they cloned the repository on their laptop:
* **macOS / Linux**:
  ```bash
  ./play.sh
  # or to specify the hub:
  python3 game.py --connect http://<ORGANIZER_IP>:5000
  ```
* **Windows**:
  ```cmd
  play.bat
  ```
*(The script automatically scans the local network via UDP beacon to discover your organizer hub without typing!).*

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
