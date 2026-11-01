#!/usr/bin/env python3
"""
game.py - Participant Game Interface for Git Workshop Day 2.
Includes full Welcome Screen (Name & Class input), Live Leaderboard updating,
Stop-on-Bingo with randomized cards, Time Tracking, First-Finisher Bonuses (+100 pts),
Locked Stage 2 (until organizer opens it), and dual Web / Terminal UI.
Zero external packages or dependencies.
"""

import sys
import os
import webbrowser
import threading
import time

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    print_box, ask_choice, ask_text, status_badge, get_terminal_width
)
from engine.state import (
    PlayerState, get_leaderboard, STAGE_NAMES, STAGE_PASSWORDS, format_seconds
)
from engine.server import start_game_server
from engine.bingo import run_bingo
from engine.detective import run_detective
from engine.branching_guide import run_branching_guide
from engine.quest import run_quest
from engine.showdown import run_showdown

def terminal_welcome_registration(state):
    """Ensure student enters their Name and Class before playing."""
    if state.is_registered():
        return
        
    clear_screen()
    print_banner("WELCOME TO THE GIT WORKSHOP ARENA", "Day 2 Interactive Games & Challenges", badge="REGISTRATION", color=Colors.BRIGHT_CYAN)
    
    welcome_text = (
        "Welcome! To join the live leaderboard and track your points & time,\n"
        "please enter your full name and class/batch below."
    )
    print_box(welcome_text, title="PLAYER REGISTRATION", color=Colors.YELLOW)
    
    while True:
        name = ask_text("Enter your Full Name")
        if name.strip():
            break
        print(f"{Colors.RED}Name cannot be empty.{Colors.RESET}")
        
    while True:
        class_name = ask_text("Enter your Class / Batch / Division (e.g. CSE-3A, 11-B)")
        if class_name.strip():
            break
        print(f"{Colors.RED}Class cannot be empty.{Colors.RESET}")
        
    state.register(name, class_name)
    print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ Registration Complete! Welcome, {state.name} ({state.class_name})!{Colors.RESET}")
    pause("Press Enter to enter the game arena...")


def print_player_hud(state):
    """Render top player HUD bar in terminal with points and total time."""
    width = get_terminal_width()
    time_str = format_seconds(state.total_time)
    hud = f" 👤 {state.name} | 🏫 {state.class_name} | 🏆 {state.score} PTS | ⏱️ TIME: {time_str} | 🎮 UNLOCKED: {len(state.unlocked_stages)}/5 "
    print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{hud.center(width)}{Colors.RESET}\n")


def view_terminal_leaderboard(state):
    """Render live leaderboard view in terminal with scores and times."""
    clear_screen()
    print_banner("GIT WORKSHOP: LIVE LEADERBOARD", "Ranked by Score • Tie-broken by Lowest Time", badge="LEADERBOARD", color=Colors.BRIGHT_MAGENTA)
    
    entries = get_leaderboard(limit=15)
    print(f"{'RANK':<6} {'NAME':<24} {'CLASS/BATCH':<16} {'SCORE':<10} {'TIME':<8}")
    print(f"{'─' * 68}")
    
    user_rank = "-"
    for idx, e in enumerate(entries, 1):
        is_user = (e.get("name") == state.name and e.get("class_name") == state.class_name)
        time_str = format_seconds(e.get("total_time", 0.0))
        if is_user:
            user_rank = idx
            prefix = f"{Colors.BRIGHT_CYAN}{Colors.BOLD}"
            badge_rank = f"▶ #{idx}"
            suffix = f"{Colors.RESET}"
        else:
            prefix = ""
            badge_rank = f"  #{idx}"
            suffix = ""
            
        print(f"{prefix}{badge_rank:<6} {e.get('name', '')[:22]:<24} {e.get('class_name', '')[:14]:<16} {e.get('score', 0):<10} {time_str:<8}{suffix}")
        
    print(f"{'─' * 68}\n")
    print(f"Your Standing: {Colors.BOLD}#{user_rank}{Colors.RESET} ({state.score} pts, Total Time: {format_seconds(state.total_time)})\n")
    pause()


def unlock_stage_dialog(state):
    """Prompt student to enter organizer stage unlock key."""
    clear_screen()
    print_banner("UNLOCK WORKSHOP STAGE", "Enter facilitator release key", badge="KEYPAD", color=Colors.YELLOW)
    print("When the workshop facilitator begins a new activity, they will display")
    print("or announce the unlock passcode on the projector screen.\n")
    
    stage_input = ask_text("Which stage do you want to unlock? (2-5)")
    try:
        stage_num = int(stage_input)
        if stage_num not in (2, 3, 4, 5):
            print(f"{Colors.RED}Stage must be 2, 3, 4, or 5.{Colors.RESET}")
            pause()
            return
    except ValueError:
        print(f"{Colors.RED}Invalid stage number.{Colors.RESET}")
        pause()
        return

    pwd = ask_text(f"Enter the unlock code for Stage {stage_num} ({STAGE_NAMES.get(stage_num)})")
    ok, msg = state.unlock_stage(stage_num, pwd)
    if ok:
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ {msg}{Colors.RESET}")
    else:
        print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✘ {msg}{Colors.RESET}")
    pause()


def run_terminal_game(state):
    """Full-featured Terminal Game Interface."""
    terminal_welcome_registration(state)
    
    while True:
        clear_screen()
        print_banner("GIT WORKSHOP ARENA: DAY 2", "Hands-on Laptop Games & Challenges", badge="GAME ARENA", color=Colors.CYAN)
        print_player_hud(state)
        
        options = []
        for s in range(1, 6):
            s_name = STAGE_NAMES[s]
            if state.is_stage_unlocked(s):
                options.append(f"▶ Stage {s}: {s_name} {Colors.BRIGHT_GREEN}[READY TO PLAY]{Colors.RESET}")
            else:
                options.append(f"🔒 Stage {s}: {s_name} {Colors.DIM}[LOCKED - Waiting for Organizer]{Colors.RESET}")
                
        options.append("🏆 View Live Leaderboard")
        options.append("🔑 Enter Organizer Stage Unlock Passcode")
        
        choice = ask_choice("Select an action:", options, allow_quit=True)
        
        if choice == -1:
            print(f"\n{Colors.CYAN}Thanks for playing, {state.name}! See you on GitHub! 🚀{Colors.RESET}\n")
            break
        elif choice == 0:
            # Stage 1: Git Bingo (Stops immediately on Bingo!)
            pts, elapsed, won = run_bingo()
            if pts or elapsed:
                new_score, is_first, bonus = state.add_game_result(1, pts, elapsed, is_completion=won)
                if is_first and bonus > 0:
                    print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}⚡⚡⚡ FIRST FINISHER SPEED BONUS! +{bonus} POINTS! ⚡⚡⚡{Colors.RESET}")
                    pause()
        elif choice == 1:
            # Stage 2: Git Detective
            if not state.is_stage_unlocked(2):
                print(f"\n{Colors.BRIGHT_RED}🔒 Stage 2 (Git Detective) is currently locked!{Colors.RESET}")
                print("The workshop organizer will unlock it on the main screen when this round starts.")
                print(f"You can also use option [7] to enter the unlock key.\n")
                pause()
            else:
                pts, elapsed, won = run_detective()
                new_score, is_first, bonus = state.add_game_result(2, pts, elapsed, is_completion=won)
                if is_first and bonus > 0:
                    print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}⚡⚡⚡ FIRST FINISHER SPEED BONUS! +{bonus} POINTS! ⚡⚡⚡{Colors.RESET}")
                    pause()
        elif choice == 2:
            # Stage 3: Branching Demo
            if not state.is_stage_unlocked(3):
                print(f"\n{Colors.BRIGHT_RED}🔒 Stage 3 (Branching) is locked! Waiting for facilitator demo.{Colors.RESET}\n")
                pause()
            else:
                start_t = time.time()
                run_branching_guide()
                elapsed = round(time.time() - start_t, 1)
                new_score, is_first, bonus = state.add_game_result(3, 20, elapsed, is_completion=True)
                if is_first and bonus > 0:
                    print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}⚡⚡⚡ FIRST FINISHER SPEED BONUS! +{bonus} POINTS! ⚡⚡⚡{Colors.RESET}")
                    pause()
        elif choice == 3:
            # Stage 4: Git Quest
            if not state.is_stage_unlocked(4):
                print(f"\n{Colors.BRIGHT_RED}🔒 Stage 4 (Git Quest) is locked! Waiting for organizer to start.{Colors.RESET}\n")
                pause()
            else:
                pts, elapsed, won = run_quest()
                new_score, is_first, bonus = state.add_game_result(4, pts, elapsed, is_completion=won)
                if is_first and bonus > 0:
                    print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}⚡⚡⚡ FIRST FINISHER SPEED BONUS! +{bonus} POINTS! ⚡⚡⚡{Colors.RESET}")
                    pause()
        elif choice == 4:
            # Stage 5: Final Showdown
            if not state.is_stage_unlocked(5):
                print(f"\n{Colors.BRIGHT_RED}🔒 Stage 5 (Final Showdown) is locked! Waiting for the grand finale.{Colors.RESET}\n")
                pause()
            else:
                pts, elapsed, won = run_showdown()
                new_score, is_first, bonus = state.add_game_result(5, pts, elapsed, is_completion=won)
                if is_first and bonus > 0:
                    print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}⚡⚡⚡ FIRST FINISHER SPEED BONUS! +{bonus} POINTS! ⚡⚡⚡{Colors.RESET}")
                    pause()
        elif choice == 5:
            view_terminal_leaderboard(state)
        elif choice == 6:
            unlock_stage_dialog(state)


def launch_web_ui(state):
    """Launch zero-dependency local web game interface."""
    server, port = start_game_server(state, port=5000)
    
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    url = f"http://localhost:{port}"
    clear_screen()
    print_banner("⚡ GIT WORKSHOP ARENA: GAME INTERFACE LAUNCHED ⚡", "Interactive Web Game Suite | Zero Dependencies", badge="ACTIVE", color=Colors.BRIGHT_CYAN)
    
    msg = (
        f"Game interface is running locally on your laptop:\n\n"
        f"  👉 URL: {Colors.BOLD}{Colors.BRIGHT_GREEN}{url}{Colors.RESET}\n\n"
        f"Opening in your web browser automatically...\n"
        f"(If your browser does not open automatically, copy and paste the URL above into Chrome, Edge, or Firefox).\n\n"
        f"• Welcome Screen will ask for your Name and Class.\n"
        f"• Live Timer records how fast you complete each challenge.\n"
        f"• Git Bingo stops immediately when you get 3 in a line!\n"
        f"• ⚡ First Finisher in every game receives a +100 Point Bonus!\n"
        f"• Stage 2 will unlock as soon as the organizer opens the round!\n\n"
        f"{Colors.DIM}Press Ctrl+C in this terminal when you want to stop the game.{Colors.RESET}"
    )
    print_box(msg, title="LOCAL GAME SERVER", color=Colors.CYAN)
    
    try:
        webbrowser.open(url)
    except Exception:
        pass
        
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Game server shut down cleanly. Thanks for playing!{Colors.RESET}\n")
        server.shutdown()


def main():
    state = PlayerState()
    if "--cli" in sys.argv or "-c" in sys.argv:
        run_terminal_game(state)
        return
    launch_web_ui(state)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Colors.RESET}Exited cleanly.")
