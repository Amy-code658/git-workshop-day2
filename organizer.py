#!/usr/bin/env python3
"""
organizer.py - Facilitator & Presenter Suite for Git Workshop Day 2.
Designed for the organizer to run on the presenter laptop connected to the projector.
Controls stage locks (e.g. unlocking Game 2: Git Detective), displays live leaderboards with time tracking,
projects clues & crime scenes, and verifies participant tokens.
Zero external dependencies (pure Python 3 standard library).
"""

import os
import sys
import time
import subprocess
import shutil

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    print_box, print_terminal_sim, ask_choice, ask_text, get_terminal_width
)
from engine.state import (
    STAGE_NAMES, STAGE_PASSWORDS, get_leaderboard, format_seconds, get_first_finishers
)
from engine.bingo import load_bingo_items
from engine.detective import load_detective_cases
from engine.quest import verify_token

ORGANIZER_STATUS = {
    "unlocked": [1],
    "current_stage": 1
}

def unlock_stage_manager():
    """Organizer stage unlock controller."""
    clear_screen()
    print_banner("ORGANIZER STAGE CONTROLLER", "Release stages for 65 participants", badge="STAGE MANAGER", color=Colors.BRIGHT_YELLOW)
    
    first_finishers = get_first_finishers()
    print("CURRENT STAGE STATUS & FIRST FINISHERS (+100 PTS BONUS):")
    for s in range(1, 6):
        is_open = s in ORGANIZER_STATUS["unlocked"]
        status_str = f"{Colors.BRIGHT_GREEN}[UNLOCKED - OPEN]{Colors.RESET}" if is_open else f"{Colors.BRIGHT_RED}[LOCKED]{Colors.RESET}"
        pwd = STAGE_PASSWORDS.get(s, "N/A")
        finisher = first_finishers.get(str(s), "None yet (100 pt bonus unclaimed!)")
        print(f"  Stage {s}: {STAGE_NAMES[s]:<20} {status_str} | Code: {Colors.BOLD}{pwd:<12}{Colors.RESET} | ⚡ 1st: {Colors.YELLOW}{finisher}{Colors.RESET}")
        
    print("\nSelect a stage to toggle unlock/lock:")
    opts = [
        f"Unlock Stage 2: Git Detective (Passcode: {STAGE_PASSWORDS[2]})",
        f"Unlock Stage 3: Branching Demo  (Passcode: {STAGE_PASSWORDS[3]})",
        f"Unlock Stage 4: Git Quest       (Passcode: {STAGE_PASSWORDS[4]})",
        f"Unlock Stage 5: Final Showdown  (Passcode: {STAGE_PASSWORDS[5]})",
        "Project Stage Unlock Codes on Screen"
    ]
    
    choice = ask_choice("Action:", opts, allow_quit=True)
    if choice == -1:
        return
    elif choice in (0, 1, 2, 3):
        stg = choice + 2
        if stg not in ORGANIZER_STATUS["unlocked"]:
            ORGANIZER_STATUS["unlocked"].append(stg)
            print(f"\n{Colors.BRIGHT_GREEN}✔ Stage {stg} ({STAGE_NAMES[stg]}) is now officially UNLOCKED!{Colors.RESET}")
            print(f"Announce passcode {Colors.BOLD}{STAGE_PASSWORDS[stg]}{Colors.RESET} to the room or project it!\n")
        else:
            print(f"\n{Colors.YELLOW}Stage {stg} is already unlocked.{Colors.RESET}\n")
        pause()
    elif choice == 4:
        project_stage_codes()


def project_stage_codes():
    """Project big unlock passcodes on the projector screen for students."""
    clear_screen()
    print_banner("WORKSHOP STAGE UNLOCK PASSCODES", "Announce or project to all participants", badge="PROJECTOR SCREEN", color=Colors.BRIGHT_CYAN)
    
    code_text = (
        f"\n"
        f"  🎯 Stage 1: Git Bingo       ➔  OPEN BY DEFAULT\n\n"
        f"  🕵️ Stage 2: Git Detective   ➔  CODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[2]}{Colors.RESET}\n\n"
        f"  🌿 Stage 3: Branching Demo  ➔  CODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[3]}{Colors.RESET}\n\n"
        f"  ⚔️ Stage 4: Git Quest (100) ➔  CODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[4]}{Colors.RESET}\n\n"
        f"  ⚡ Stage 5: Final Showdown  ➔  CODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[5]}{Colors.RESET}\n"
    )
    print_box(code_text, title="ORGANIZER RELEASE KEYS", color=Colors.BRIGHT_YELLOW)
    print(f"\n{Colors.DIM}Students can type the matching code on their laptops to unlock each round!{Colors.RESET}")
    pause()


def projector_master_leaderboard():
    """Fullscreen projector leaderboard with scores and total elapsed times."""
    clear_screen()
    print_banner("GIT WORKSHOP ARENA: OFFICIAL LEADERBOARD", "Ranked by Score • Tie-broken by Lowest Time", badge="LIVE RANKINGS", color=Colors.BRIGHT_MAGENTA)
    
    entries = get_leaderboard(limit=25)
    width = min(get_terminal_width(), 86)
    
    print(f"{'RANK':<8} {'STUDENT NAME':<26} {'CLASS / BATCH':<18} {'SCORE':<12} {'TOTAL TIME'}")
    print(f"{'═' * width}")
    
    if not entries:
        print(f"\n  {Colors.DIM}No scores registered yet. As students complete challenges, scores appear here!{Colors.RESET}\n")
    else:
        for idx, e in enumerate(entries, 1):
            if idx == 1:
                rank_str = "🥇 1ST"
                color = Colors.BRIGHT_YELLOW + Colors.BOLD
            elif idx == 2:
                rank_str = "🥈 2ND"
                color = Colors.WHITE + Colors.BOLD
            elif idx == 3:
                rank_str = "🥉 3RD"
                color = Colors.YELLOW + Colors.BOLD
            else:
                rank_str = f"  #{idx:<4}"
                color = Colors.WHITE
                
            name_str = e.get("name", "Student")[:24]
            class_str = e.get("class_name", "--")[:16]
            score_str = f"{e.get('score', 0)} PTS"
            time_str = f"⏱️ {format_seconds(e.get('total_time', 0.0))}"
            
            print(f"{color}{rank_str:<8} {name_str:<26} {class_str:<18} {Colors.BRIGHT_GREEN}{score_str:<12}{Colors.RESET} {time_str}")
            
    print(f"{'═' * width}\n")
    pause("Press Enter to return to organizer menu...")


def projector_bingo():
    """Projector view for 3:30–3:45 Git Bingo."""
    items = load_bingo_items()
    clear_screen()
    print_banner("ORGANIZER PROJECTOR: GIT BINGO ROUND", "Present clues on the big screen & reveal answers", badge="PROJECTOR MODE", color=Colors.BRIGHT_MAGENTA)
    print("Project your terminal on the big screen.")
    print("Display each clue, give students 15–30 seconds to check their unique 3x3 cards,")
    print("then press Enter to reveal the correct command and explanation.\n")
    pause("Press Enter to begin Question 1...")

    for i, item in enumerate(items, 1):
        clear_screen()
        badge = f"CLUE {i} OF {len(items)}"
        print_banner(f"GIT BINGO: QUESTION {i}", "Identify the matching Git command", badge=badge, color=Colors.CYAN)
        
        prompt_box = f"\n  {Colors.BOLD}{Colors.BRIGHT_YELLOW}{item['prompt']}{Colors.RESET}\n"
        print_box(prompt_box, title=f"CLUE #{i}", color=Colors.BRIGHT_YELLOW)
        
        print(f"\n{Colors.DIM}>> Students: Check your card! If you complete 3 in a line, you get BINGO immediately! <<{Colors.RESET}")
        pause("\nPress Enter to REVEAL ANSWER...")
        
        answer_box = (
            f"COMMAND:      {Colors.BOLD}{Colors.BRIGHT_GREEN}{item['command']}{Colors.RESET}\n\n"
            f"EXPLANATION:  {item['explanation']}"
        )
        print_box(answer_box, title="✔ OFFICIAL ANSWER REVEAL", color=Colors.BRIGHT_GREEN)
        
        pause("Press Enter for the next clue...")

    clear_screen()
    print_banner("GIT BINGO PROJECTOR ROUND COMPLETE", "All questions presented", badge="FINISHED", color=Colors.GREEN)
    pause()


def projector_detective():
    """Projector view for 3:45–4:10 Git Detective."""
    cases = load_detective_cases()
    clear_screen()
    print_banner("ORGANIZER PROJECTOR: GIT DETECTIVE", "Display crime scenes on screen for room-wide diagnosis", badge="PROJECTOR MODE", color=Colors.YELLOW)
    print("Display terminal outputs on the projector.")
    print("Give the students 30–60 seconds to analyze the situation,")
    print("then press Enter to reveal the diagnosis, correct fix, and developer tip.\n")
    pause("Press Enter to begin Case 1...")

    for i, case in enumerate(cases, 1):
        clear_screen()
        badge = f"CASE {i} OF {len(cases)}"
        print_banner(f"CASE #{i}: {case['title'].upper()}", f"Difficulty: {case['difficulty']}", badge=badge, color=Colors.YELLOW)
        
        print_box(case["scenario"], title="THE SITUATION", color=Colors.CYAN)
        print_terminal_sim(case["command_sim"], case["output_sim"], title="PROJECTED TERMINAL EVIDENCE")
        
        print(f"{Colors.BOLD}{case['question']}{Colors.RESET}\n")
        for opt_idx, opt in enumerate(case["options"], 1):
            print(f"  {Colors.YELLOW}[{opt_idx}]{Colors.RESET} {opt}")
            
        print(f"\n{Colors.DIM}>> Students are choosing their answers now (30-60s) <<{Colors.RESET}")
        pause("\nPress Enter to REVEAL CORRECT DIAGNOSIS...")
        
        correct_text = case["options"][case["correct_index"]]
        reveal_box = (
            f"CORRECT CHOICE: {Colors.BOLD}{Colors.BRIGHT_GREEN}[{case['correct_index'] + 1}] {correct_text}{Colors.RESET}\n\n"
            f"DIAGNOSIS:     {case['explanation']}\n\n"
            f"PRO-TIP:       {case.get('pro_tip', '')}"
        )
        print_box(reveal_box, title="✔ CASE REVEAL & EXPLANATION", color=Colors.BRIGHT_GREEN)
        
        pause("Press Enter for the next case...")

    clear_screen()
    print_banner("GIT DETECTIVE PROJECTOR ROUND COMPLETE", "All cases investigated", badge="FINISHED", color=Colors.GREEN)
    pause()


def projector_demo_companion():
    """Presenter guide & companion for 4:10–4:40 Branching & Merging Demo."""
    clear_screen()
    print_banner("FACILITATOR DEMO SCRIPT: BRANCHING & MERGING", "4:10–4:40 Demonstration Checklist", badge="PRESENTER SCRIPT", color=Colors.BRIGHT_BLUE)
    
    script = (
        "STEP-BY-STEP LIVE DEMONSTRATION FLOW:\n\n"
        "1. Explain WHY we branch:\n"
        "   - Protect working code on 'main'\n"
        "   - Allow multiple students/devs to work in parallel\n\n"
        "2. Run live in your terminal:\n"
        "   $ git switch -c add-my-section\n"
        "   (Explain what -c does: creates and checks out the branch)\n\n"
        "3. Edit README.md:\n"
        "   - Open README.md and add a section header\n"
        "   - Show 'git status' to highlight the red modified file\n\n"
        "4. Stage and commit:\n"
        "   $ git add README.md\n"
        "   $ git commit -m \"Add contributor section\"\n"
        "   (Show 'git log -1' to show the commit on the branch)\n\n"
        "5. Push upstream to GitHub:\n"
        "   $ git push -u origin add-my-section\n"
        "   (Explain the -u flag setting upstream tracking)\n\n"
        "6. Switch to browser (projector):\n"
        "   - Show the yellow 'Compare & pull request' banner on GitHub\n"
        "   - Open the PR, show the diff, discuss code review\n"
        "   - Click 'Merge pull request' and 'Confirm merge'!\n\n"
        "7. Sync local main:\n"
        "   $ git switch main\n"
        "   $ git pull\n"
        "   (Show students that the merged code is now on local main!)"
    )
    print_box(script, title="PRESENTER CHEAT SHEET", color=Colors.CYAN)
    pause()


def token_verifier_tool():
    """Verify participant Git Quest codes."""
    clear_screen()
    print_banner("GIT QUEST CODE VERIFIER", "Instantly validate student submission codes", badge="ORGANIZER TOOL", color=Colors.BRIGHT_GREEN)
    print("Students who complete Activity D (Git Quest) receive an official verification code.")
    print("Example: GQ-100-TAYLOR-A4B2\n")
    
    while True:
        token = ask_text("Enter student verification code (or 'q' to return)")
        if token.lower() in ("q", "quit", "exit"):
            break
        if not token:
            continue
            
        valid, msg = verify_token(token)
        if valid:
            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ VALID SUBMISSION!{Colors.RESET}")
            print(f"{Colors.GREEN}{msg}{Colors.RESET}\n")
        else:
            print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✘ VERIFICATION FAILED!{Colors.RESET}")
            print(f"{Colors.RED}{msg}{Colors.RESET}\n")


def generate_sandbox_repo():
    """Create a temporary practice git repo for demonstrations or testing."""
    clear_screen()
    print_banner("SANDBOX REPOSITORY GENERATOR", "Instantly spin up a practice Git workspace", badge="SETUP TOOL", color=Colors.YELLOW)
    
    default_path = os.path.join(os.getcwd(), "git-practice-sandbox")
    path = ask_text("Enter directory to create sandbox repo in", default=default_path)
    target_dir = os.path.abspath(os.path.expanduser(path))
    
    if os.path.exists(target_dir):
        overwrite = ask_choice(f"Directory '{target_dir}' already exists. Overwrite?", ["Yes, recreate sandbox", "Cancel"], allow_quit=False)
        if overwrite == 0:
            shutil.rmtree(target_dir, ignore_errors=True)
        else:
            return

    os.makedirs(target_dir, exist_ok=True)
    subprocess.run(["git", "init"], cwd=target_dir, check=True)
    
    readme_path = os.path.join(target_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Git Workshop Practice Project\n\nWelcome to Day 2! Use this repository to practice branching, staging, and commits.\n")
        
    subprocess.run(["git", "add", "README.md"], cwd=target_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit: Add README.md"], cwd=target_dir, check=True)
    
    print(f"\n{Colors.BRIGHT_GREEN}✔ Sandbox repository successfully created at:{Colors.RESET}")
    print(f"{Colors.BOLD}{target_dir}{Colors.RESET}\n")
    pause()


def organizer_menu():
    """Main Organizer Dashboard."""
    while True:
        clear_screen()
        print_banner(
            "GIT WORKSHOP: ORGANIZER & FACILITATOR DASHBOARD",
            "Controls, Stage Unlocks & Master Projector Views",
            badge="PRESENTER MODE",
            color=Colors.BRIGHT_YELLOW
        )
        
        options = [
            "🔓 Stage Unlock Controller (Release Stage 2, 3, 4, 5 & View 1st Finishers)",
            "🏆 Projector View: Live Master Leaderboard (Scores & Times)",
            "🔑 Project Stage Unlock Codes (Big Screen Display)",
            "📽️  Projector View: Git Bingo (Clues & Answer Reveals)",
            "📽️  Projector View: Git Detective (Crime Scenes & Reveals)",
            "📋 Presenter Script: Branching & Merging Demo (4:10–4:40)",
            "🔑 Git Quest Token Verifier (Check Student Codes)",
            "📦 Generate Practice Sandbox Git Repository"
        ]
        
        choice = ask_choice("Select an organizer function:", options, allow_quit=True)
        
        if choice == -1:
            break
        elif choice == 0:
            unlock_stage_manager()
        elif choice == 1:
            projector_master_leaderboard()
        elif choice == 2:
            project_stage_codes()
        elif choice == 3:
            projector_bingo()
        elif choice == 4:
            projector_detective()
        elif choice == 5:
            projector_demo_companion()
        elif choice == 6:
            token_verifier_tool()
        elif choice == 7:
            generate_sandbox_repo()

if __name__ == "__main__":
    try:
        organizer_menu()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Colors.RESET}Exited cleanly.")
