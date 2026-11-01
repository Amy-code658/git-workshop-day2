# 🎮 Git Workshop Arena — Day 2: Terminal Games & Challenges

An immersive, zero-dependency game interface built specifically for **Day 2 of the Git Workshop** (designed for ~65 laptop participants and the workshop organizer).

Runs directly on **any laptop** (Windows, macOS, Linux) with **pure Python 3 standard library**. No `pip install`, no node/npm, and no internet access required to run.

---

## ⚡ Key Highlights & Security Rules

* **Interactive Game Interface**: Rich visual arena with top HUD (`Player Name`, `Class`, `Score`, `Rank`), sound effects (Web Audio API), animated scoreboards, and instant feedback.
* **Welcome Screen & Registration**: Prompts each participant for their **Full Name** and **Class / Division** before entering, instantly placing them into the live workshop leaderboard.
* **Live Dynamic Leaderboard**: Updates each student's score in real time as they complete Bingo squares, solve detective cases, inspect repositories, and answer questions.
* **Stage Access Control (Locked Stage 2)**:
  * Stage 1 (*Git Bingo*) is available immediately.
  * Stage 2 (*Git Detective*) and subsequent stages are **LOCKED** until the organizer unlocks them!
  * If a student tries to access a locked stage, it informs them to wait for the facilitator or enter the release code.
* **No Organizer Bypass for Students**:
  * The student interface contains **zero links or options** to skip into organizer settings or alter game locks.
  * The organizer suite is kept completely separate in `organizer.py`.

---

## 🚀 Quickstart

### For Participants / Students

Clone or download this folder, open your terminal inside it, and run:

* **macOS / Linux:**
  ```bash
  ./play.sh
  # or
  python3 game.py
  ```

* **Windows (Command Prompt / PowerShell):**
  ```cmd
  play.bat
  :: or
  python game.py
  ```

> 💡 **Terminal Mode**: To play completely inside your terminal without opening a browser, run:  
> `python3 game.py --cli`

---

### For the Organizer / Facilitator

Connect your laptop to the venue projector and run:

```bash
python3 organizer.py
# (or python organizer.py on Windows)
```

The **Organizer Dashboard** gives you:
1. **🔓 Stage Unlock Controller**: Unlock Stage 2 (*Git Detective*), Stage 3, Stage 4, or Stage 5 with one keystroke!
2. **🏆 Projector Master Leaderboard**: Fullscreen real-time rankings of all 65 students by points and class.
3. **🔑 Project Stage Unlock Codes**: Display the release passcodes (e.g. `DETECTIVE26`) in giant high-contrast text on the projector screen for offline participant unlocking.
4. **📽️ Projector Clues & Case Reveals**: Display Bingo clues and Detective terminal crime scenes to the entire room, then press Enter to reveal the official explanation.
5. **🔑 Git Quest Token Verifier**: Validate student submission tokens (e.g. `GQ-100-NAME-XXXX`).
6. **📦 Sandbox Generator**: Spin up a sample Git repo on demand for the 4:10 PM branching demo.

---

## ⏰ Day 2 Schedule & Activity Breakdown

| Time | Session | What Participants Do | Stage Status |
| :--- | :--- | :--- | :---: |
| **3:30–3:45** | **Git Bingo (Laptop Edition)** | Match Git concepts to commands on a 3x3 interactive card. Line up 3 in a row for a 50-pt BINGO! | **UNLOCKED** |
| **3:45–4:10** | **Git Detective** | Inspect real terminal crime scenes. Diagnose failed commits, unstaged files, and pick the right command. | **🔒 LOCKED** *(Organizer opens)* |
| **4:10–4:40** | **Branching & Merging** | Follow along with the facilitator's live demonstration of branching, committing, pushing, and Pull Requests. | **🔒 LOCKED** *(Organizer opens)* |
| **4:40–5:10** | **Git Quest (100-Pt Challenge)** | Automated inspection engine that tests your actual local practice repository and grades all 7 tasks. | **🔒 LOCKED** *(Organizer opens)* |
| **5:10–5:30** | **Final Showdown & Wrap-Up** | 10 rapid-fire questions testing speed, accuracy, and streaks. Generates an end-of-workshop achievement report. | **🔒 LOCKED** *(Organizer opens)* |

---

## 🏆 Git Quest Rubric (100 Points Total)

The automated `Git Quest` checker inspects your local repository non-destructively:

| Task | What Is Evaluated | Points |
| :--- | :--- | :---: |
| **1. Check repository status** | Valid initialized Git repository (`git status`) | **10 pts** |
| **2. Create a branch** | Non-default branch created (`git switch -c`) | **10 pts** |
| **3. Edit a file** | `README.md` created or updated | **10 pts** |
| **4. Stage and commit** | Valid commit log history (`git commit`) | **15 pts** |
| **5. Push the branch** | Remote tracking branch linked to GitHub (`git push -u origin <branch>`) | **15 pts** |
| **6. Open a pull request** | Pull request opened on GitHub | **20 pts** |
| **7. Review the change** | PR review and merge into main | **20 pts** |
| **TOTAL** | **Maximum Achievable Score** | **100 pts** |

---

## 📁 Repository Structure

```text
git-workshop-day2/
├── README.md               # Workshop guide and instructions
├── play.sh                 # One-click launcher for macOS / Linux
├── play.bat                # One-click launcher for Windows
├── game.py                 # Main participant runner (Web & CLI modes)
├── organizer.py            # Facilitator / Projector dashboard
├── web/                    # Built-in Game Interface (Zero external CDNs)
│   ├── index.html          # Registration, HUD, Cards, Modals, Leaderboard
│   ├── style.css           # Retro arcade cyberpunk styling
│   └── game.js             # Game engine & Web Audio sound synthesizer
└── engine/                 # Core game engines (Standard Library only)
    ├── __init__.py
    ├── state.py            # Player profiles, stage locks & live leaderboard sync
    ├── server.py           # Zero-dependency local REST API & static server
    ├── ui.py               # Cross-platform ANSI terminal styling & boxes
    ├── bingo.py            # Activity A: 3x3 Git Bingo engine
    ├── detective.py        # Activity B: Git Detective crime scene cases
    ├── branching_guide.py  # Activity C: Interactive branching companion
    ├── quest.py            # Activity D: Real-time 100-pt repo grader & token issuer
    ├── showdown.py         # Activity E: Rapid-fire review quiz & streaks
    └── content/            # Customizable question & scenario JSON data
        ├── bingo_data.json
        ├── detective_cases.json
        └── showdown_questions.json
```
