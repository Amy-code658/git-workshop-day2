#!/usr/bin/env python3
"""
organizer.py - Facilitator & Presenter Suite for Git Workshop Day 2.
Designed for the organizer to run on the presenter laptop connected to the projector.
Includes Projector Slide Modes, Answer Reveals, Quest Code Verifier, and Demo Sandbox Generator.
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
    print_box, print_terminal_sim, ask_choice, ask_text
)
from engine.bingo import load_bingo_items
from engine.detective import load_detective_cases
from engine.showdown import load_showdown_questions
from engine.quest import verify_token

def projector_bingo():
    """Projector view for 3:30–3:45 Git Bingo."""
    items = load_bingo_items()
    clear_screen()
    print_banner("ORGANIZER PROJECTOR: GIT BINGO ROUND", "Present clues on the big screen & reveal answers", badge="PROJECTOR MODE", color=Colors.BRIGHT_MAGENTA)
    print("In this mode, project your terminal on the big screen.")
    print("Display each clue, give students 15–30 seconds to pick the command on their laptops,")
    print("then press Enter to reveal the correct command and explanation.\n")
    pause("Press Enter to begin Question 1...")

    for i, item in enumerate(items, 1):
        clear_screen()
        badge = f"CLUE {i} OF {len(items)}"
        print_banner(f"GIT BINGO: QUESTION {i}", "Identify the matching Git command", badge=badge, color=Colors.CYAN)
        
        # Display Prompt in large prominent box
        prompt_box = (
            f"\n  {Colors.BOLD}{Colors.BRIGHT_YELLOW}{item['prompt']}{Colors.RESET}\n"
        )
        print_box(prompt_box, title=f"CLUE #{i}", color=Colors.BRIGHT_YELLOW)
        
        print(f"\n{Colors.DIM}>> Students: Select the matching command on your 3x3 Bingo grid! <<{Colors.RESET}")
        pause("\nPress Enter to REVEAL ANSWER...")
        
        # Reveal Answer & Explanation
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
    print("Give the 65 students 30–60 seconds to analyze the situation,")
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
    
    # Initialize repo
    subprocess.run(["git", "init"], cwd=target_dir, check=True)
    
    # Create sample files
    readme_path = os.path.join(target_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Git Workshop Practice Project\n\nWelcome to Day 2! Use this repository to practice branching, staging, and commits.\n")
        
    subprocess.run(["git", "add", "README.md"], cwd=target_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit: Add README.md"], cwd=target_dir, check=True)
    
    print(f"\n{Colors.BRIGHT_GREEN}✔ Sandbox repository successfully created at:{Colors.RESET}")
    print(f"{Colors.BOLD}{target_dir}{Colors.RESET}\n")
    print("Files created:")
    print("  • README.md (staged and committed on initial branch)")
    print(f"\nYou can now test 'python game.py quest' or run demo commands inside this directory!\n")
    pause()


def organizer_menu():
    """Main Organizer / Facilitator Dashboard."""
    while True:
        clear_screen()
        print_banner(
            "GIT WORKSHOP: ORGANIZER & FACILITATOR DASHBOARD",
            "Projector Display Controls, Demo Scripts & Student Code Verification",
            badge="PRESENTER MODE",
            color=Colors.BRIGHT_YELLOW
        )
        
        options = [
            "📽️  Projector View: Git Bingo (Clues & Answer Reveals)",
            "📽️  Projector View: Git Detective (Crime Scenes & Reveals)",
            "📋 Presenter Script: Branching & Merging Demo (4:10–4:40)",
            "🔑 Git Quest Token Verifier (Check Student Codes)",
            "📦 Generate Practice Sandbox Git Repository",
            "🔄 Switch to Participant / Student Mode"
        ]
        
        choice = ask_choice("Select an organizer function:", options, allow_quit=True)
        
        if choice == -1:
            break
        elif choice == 0:
            projector_bingo()
        elif choice == 1:
            projector_detective()
        elif choice == 2:
            projector_demo_companion()
        elif choice == 3:
            token_verifier_tool()
        elif choice == 4:
            generate_sandbox_repo()
        elif choice == 5:
            import game
            game.main_menu()

if __name__ == "__main__":
    try:
        organizer_menu()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Colors.RESET}Exited cleanly.")
