# 🎮 Git Workshop — Day 2: Terminal Games & Challenges

An interactive, zero-dependency terminal suite built specifically for **Day 2 of the Git Workshop** (designed for ~65 laptop participants and the workshop organizer).

Runs directly in the command prompt or terminal of **any laptop** (Windows, macOS, Linux) with **pure Python 3 standard library**. No `pip install`, no virtual environments, and no internet access required to run the games.

---

## 🚀 Quickstart

### For Participants / Students

Clone or download this folder onto your laptop, open your terminal inside it, and run:

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

---

### For the Organizer / Facilitator

Connect your laptop to the projector and run:

```bash
python3 organizer.py
# (or python organizer.py on Windows)
```

This launches the **Organizer Dashboard** featuring:
1. **Projector View for Git Bingo**: Large-text clues for the room, followed by single-key answer and explanation reveals.
2. **Projector View for Git Detective**: Large simulated terminal outputs ("crime scenes") for room-wide diagnosis and guided explanations.
3. **Branching & Merging Demo Script**: The exact 6-step collaborative demo sequence with copy-pasteable commands.
4. **Git Quest Code Verifier**: Instant validation of student submission tokens (e.g. `GQ-100-ALEX-8B3F`) to verify their 100-point achievements without inspecting 65 separate laptops.
5. **Sandbox Repository Generator**: Instantly creates a clean practice Git repository for demonstrations.

---

## ⏰ Day 2 Schedule & Activity Breakdown

| Time | Session | What Participants Do | Terminal Activity |
| :--- | :--- | :--- | :--- |
| **3:30–3:45** | **Git Bingo (Laptop Edition)** | Match Git concepts to commands on a 3x3 terminal Bingo card. Connect 3 in a line for bonus points! | `python3 game.py bingo` |
| **3:45–4:10** | **Git Detective** | Inspect real-world terminal errors and outputs. Diagnose why commits failed, identify branches, and choose fixes. | `python3 game.py detective` |
| **4:10–4:40** | **Branching & Merging** | Follow along with the facilitator's live demonstration of branching, committing, pushing, and Pull Requests. | `python3 game.py guide` |
| **4:40–5:10** | **Git Quest (100-Pt Challenge)** | Automated inspection engine that tests your actual local practice repository and grades all 7 tasks. | `python3 game.py quest` |
| **5:10–5:30** | **Final Showdown & Wrap-Up** | 10 rapid-fire questions testing speed, accuracy, and streaks. Generates an end-of-workshop achievement report. | `python3 game.py showdown` |

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

Upon completion, students receive a tamper-evident **Verification Code** (e.g., `GQ-100-NAME-XXXX`) to submit to the organizer!

---

## 📁 Repository Structure

```text
git-workshop-day2/
├── README.md               # Workshop guide and instructions
├── play.sh                 # One-click launcher for macOS / Linux
├── play.bat                # One-click launcher for Windows
├── game.py                 # Main student runner and interactive menu
├── organizer.py            # Facilitator / Projector dashboard
└── engine/                 # Core game engines (Standard Library only)
    ├── __init__.py
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

---

## 🛡️ Key Features & Compatibility

* **Zero External Dependencies**: Standard library Python 3 only (`sys`, `os`, `json`, `subprocess`, `time`, `random`, `hashlib`).
* **Cross-Platform Compatibility**: Tested and styled for Windows (Command Prompt, PowerShell, Git Bash, Windows Terminal), macOS (Terminal, iTerm), and Linux.
* **Smart Color Detection**: Automatically detects ANSI support and falls back to clean plain-text borders if run in legacy environments without color support.
* **100% Offline Capable**: All games and validators run locally. If venue Wi-Fi becomes spotty or disconnects, the workshop continues without interruption!
