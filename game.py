#!/usr/bin/env python3
"""
game.py - Main entrypoint for Git Workshop Day 2 Games & Challenges.
Designed for ~65 laptop participants. Pure Python 3 standard library.
Works on Windows, macOS, and Linux without any external packages.
"""

import sys
import os

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.ui import Colors, clear_screen, pause, print_banner, ask_choice, print_box
from engine.bingo import run_bingo
from engine.detective import run_detective
from engine.branching_guide import run_branching_guide
from engine.quest import run_quest
from engine.showdown import run_showdown

def run_all_gauntlet():
    """Run all Day 2 activities in sequential order."""
    clear_screen()
    print_banner("THE DAY 2 GAUNTLET", "Full sequential workshop adventure", badge="ALL ACTIVITIES", color=Colors.BRIGHT_MAGENTA)
    print("You are about to experience the entire Day 2 program:")
    print("  1. Git Bingo (Match terms & commands)")
    print("  2. Git Detective (Solve mystery terminal errors)")
    print("  3. Branching & Merging Walkthrough")
    print("  4. Git Quest (Automated 100-pt Repo Evaluator)")
    print("  5. The Final Showdown (Rapid-fire quiz)")
    pause("Press Enter when you are ready to begin...")
    
    score_bingo = run_bingo()
    score_det = run_detective()
    run_branching_guide()
    score_quest = run_quest()
    score_show = run_showdown()
    
    total_score = score_bingo + score_det + score_quest + score_show
    
    clear_screen()
    print_banner("WORKSHOP DAY 2 CONQUERED!", f"Grand Total Score: {total_score} points", badge="GRAND FINALE", color=Colors.GREEN)
    summary = (
        f"Git Bingo:       {score_bingo} pts\n"
        f"Git Detective:   {score_det} pts\n"
        f"Git Quest:       {score_quest} / 100 pts\n"
        f"Final Showdown:  {score_show} pts\n"
        f"{'─' * 30}\n"
        f"TOTAL COMBINED:  {total_score} PTS\n\n"
        f"Congratulations on completing Day 2 of the Git Workshop!"
    )
    print_box(summary, title="MASTER SCORECARD", color=Colors.BRIGHT_CYAN)
    pause()

def main_menu():
    """Main interactive menu for participants."""
    while True:
        clear_screen()
        print_banner(
            "GIT WORKSHOP: DAY 2 GAMES & CHALLENGES",
            "Interactive Terminal Suite for 65 Participants | Zero Dependencies",
            badge="STUDENT MODE",
            color=Colors.CYAN
        )
        
        options = [
            "🎯 Git Bingo (3:30–3:45) - Match concepts on a 3x3 card",
            "🕵️  Git Detective (3:45–4:10) - Diagnose real terminal error scenes",
            "🌿 Branching & Merging (4:10–4:40) - Interactive demo walkthrough",
            "⚔️  Git Quest (4:40–5:10) - Automated 100-pt repository grader",
            "⚡ The Final Showdown (5:10–5:30) - Rapid-fire review quiz & certificate",
            "🚀 Day 2 Full Gauntlet - Play all activities sequentially",
            "🛠️  Switch to Organizer / Projector Mode"
        ]
        
        choice = ask_choice("Select an activity to launch:", options, allow_quit=True)
        
        if choice == -1:
            print(f"\n{Colors.CYAN}Thank you for participating in the Git Workshop! Keep on committing! 🚀{Colors.RESET}\n")
            break
        elif choice == 0:
            run_bingo()
        elif choice == 1:
            run_detective()
        elif choice == 2:
            run_branching_guide()
        elif choice == 3:
            run_quest()
        elif choice == 4:
            run_showdown()
        elif choice == 5:
            run_all_gauntlet()
        elif choice == 6:
            import organizer
            organizer.organizer_menu()

def cli_entrypoint():
    """Allow direct sub-command launches: python game.py [bingo|detective|quest|showdown|organizer]."""
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower().strip("-")
        if cmd == "bingo":
            run_bingo()
            return
        elif cmd in ("detective", "cases"):
            run_detective()
            return
        elif cmd in ("branch", "guide"):
            run_branching_guide()
            return
        elif cmd in ("quest", "grade"):
            run_quest()
            return
        elif cmd in ("showdown", "quiz"):
            run_showdown()
            return
        elif cmd in ("organizer", "host", "presenter"):
            import organizer
            organizer.organizer_menu()
            return
        elif cmd in ("help", "h"):
            print("Usage: python game.py [bingo|detective|guide|quest|showdown|organizer]")
            return
            
    main_menu()

if __name__ == "__main__":
    try:
        cli_entrypoint()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Colors.RESET}Exited cleanly.")
