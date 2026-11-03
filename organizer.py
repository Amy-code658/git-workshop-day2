#!/usr/bin/env python3
"""
organizer.py - Facilitator & Presenter Suite for FOSS MEC Git Workshop Day 2.
Runs the central workshop hub server, controls stage locks (e.g. unlocking Game 2: Git Detective),
displays live room-wide leaderboards with time tracking, and projects clues/scenarios.
Zero external dependencies (pure Python 3 standard library).
"""

import os
import sys
import time
import subprocess
import shutil
import threading

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    print_box, print_terminal_sim, ask_choice, ask_text, get_terminal_width
)
from engine.state import (
    STAGE_NAMES, STAGE_PASSWORDS, get_leaderboard, format_seconds,
    get_first_finishers, get_workshop_status, set_workshop_status,
    reset_leaderboard, get_lan_ip
)
from engine.server import start_hub_server
from engine.bingo import load_bingo_items
from engine.detective import load_detective_cases
from engine.quest import verify_token

# Background server handle
HUB_SERVER = None
HUB_PORT = 5000
HUB_IP = get_lan_ip()

def ensure_hub_running():
    """Ensure the Central Workshop Hub Server is running in the background."""
    global HUB_SERVER, HUB_PORT
    if HUB_SERVER is None:
        try:
            HUB_SERVER, HUB_PORT = start_hub_server(port=5000, start_beacon=True)
            t = threading.Thread(target=HUB_SERVER.serve_forever, daemon=True)
            t.start()
        except Exception as e:
            print(f"Warning: Could not start central hub on port 5000: {e}")

def print_hub_header():
    """Print the connection address banner for projector and students."""
    lan_ip = get_lan_ip()
    width = min(get_terminal_width(), 84)
    print(f"{Colors.BG_BLUE}{Colors.BRIGHT_WHITE}{' 🌐 FOSS MEC WORKSHOP HUB ACTIVE '.center(width)}{Colors.RESET}")
    print(f"  {Colors.BOLD}Projector URL:{Colors.RESET}   {Colors.BRIGHT_GREEN}http://localhost:{HUB_PORT}{Colors.RESET}")
    print(f"  {Colors.BOLD}Student URL:{Colors.RESET}     {Colors.BRIGHT_YELLOW}{Colors.BOLD}http://{lan_ip}:{HUB_PORT}{Colors.RESET} (Open on any laptop / phone)")
    print(f"{Colors.DIM}{'─' * width}{Colors.RESET}\n")

def unlock_stage_manager():
    """Organizer stage unlock controller that instantly broadcasts to all laptops."""
    clear_screen()
    print_banner("STAGE CONTROLLER & LIVE BROADCAST", "Unlocks reflect immediately on all student laptops", badge="STAGE MANAGER", color=Colors.BRIGHT_YELLOW)
    print_hub_header()
    
    st = get_workshop_status()
    unlocked = st.get("unlocked", [1])
    first_finishers = get_first_finishers()

    print("CURRENT WORKSHOP STAGE STATUS:")
    for s in range(1, 6):
        is_open = s in unlocked
        status_str = f"{Colors.BRIGHT_GREEN}[UNLOCKED - LIVE]{Colors.RESET}" if is_open else f"{Colors.BRIGHT_RED}[LOCKED]{Colors.RESET}"
        pwd = STAGE_PASSWORDS.get(s, "N/A")
        finisher = first_finishers.get(str(s), "Unclaimed (+100 pt bonus)")
        print(f"  Stage {s}: {STAGE_NAMES[s]:<20} {status_str} | Passcode: {Colors.BOLD}{pwd:<12}{Colors.RESET} | ⚡ 1st: {Colors.YELLOW}{finisher}{Colors.RESET}")
        
    print("\nSelect a stage to toggle unlock/lock (reflects on all student screens within 2s):")
    opts = [
        f"Unlock Stage 2: Git Detective (Passcode: {STAGE_PASSWORDS[2]})",
        f"Unlock Stage 3: Branching Demo  (Passcode: {STAGE_PASSWORDS[3]})",
        f"Unlock Stage 4: Git Quest       (Passcode: {STAGE_PASSWORDS[4]})",
        f"Unlock Stage 5: Final Showdown  (Passcode: {STAGE_PASSWORDS[5]})",
        "Lock a Stage",
        "Project Stage Unlock Codes on Big Screen"
    ]
    
    choice = ask_choice("Action:", opts, allow_quit=True)
    if choice == -1:
        return
    elif choice in (0, 1, 2, 3):
        stg = choice + 2
        if stg not in unlocked:
            unlocked.append(stg)
            set_workshop_status(unlocked, current_stage=stg)
            print(f"\n{Colors.BRIGHT_GREEN}✔ Stage {stg} ({STAGE_NAMES[stg]}) is now officially UNLOCKED!{Colors.RESET}")
            print(f"All student screens will update automatically within 2 seconds!\n")
        else:
            print(f"\n{Colors.YELLOW}Stage {stg} is already unlocked.{Colors.RESET}\n")
        pause()
    elif choice == 4:
        stg_in = ask_text("Enter stage number to lock (2-5)")
        try:
            s_num = int(stg_in)
            if s_num in unlocked and s_num != 1:
                unlocked.remove(s_num)
                set_workshop_status(unlocked)
                print(f"\n{Colors.RED}Stage {s_num} locked.{Colors.RESET}")
        except ValueError:
            pass
        pause()
    elif choice == 5:
        project_stage_codes()


def project_stage_codes():
    """Project big unlock passcodes on the projector screen for students."""
    clear_screen()
    lan_ip = get_lan_ip()
    print_banner("FOSS MEC: STAGE UNLOCK PASSCODES", "Announce or project to all participants", badge="PROJECTOR SCREEN", color=Colors.BRIGHT_CYAN)
    
    code_text = (
        f"\n"
        f"  🌐 Connect to Arena at:  {Colors.BOLD}{Colors.BRIGHT_YELLOW}http://{lan_ip}:{HUB_PORT}{Colors.RESET}\n\n"
        f"  🎯 Stage 1: Git Bingo       ➔  OPEN BY DEFAULT\n\n"
        f"  🕵️ Stage 2: Git Detective   ➔  PASSCODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[2]}{Colors.RESET}\n\n"
        f"  🌿 Stage 3: Branching Demo  ➔  PASSCODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[3]}{Colors.RESET}\n\n"
        f"  ⚔️ Stage 4: Git Quest (100) ➔  PASSCODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[4]}{Colors.RESET}\n\n"
        f"  ⚡ Stage 5: Final Showdown  ➔  PASSCODE:  {Colors.BOLD}{Colors.BRIGHT_GREEN}{STAGE_PASSWORDS[5]}{Colors.RESET}\n"
    )
    print_box(code_text, title="ORGANIZER RELEASE KEYS", color=Colors.BRIGHT_YELLOW)
    pause()


def projector_master_leaderboard():
    """Fullscreen projector leaderboard updating live."""
    clear_screen()
    print_banner("FOSS MEC: LIVE WORKSHOP LEADERBOARD", "Real-Time Room Rankings (Ties broken by Lowest Time)", badge="LIVE RANKINGS", color=Colors.BRIGHT_MAGENTA)
    print_hub_header()
    
    entries = get_leaderboard(limit=30)
    width = min(get_terminal_width(), 86)
    
    print(f"{'RANK':<8} {'STUDENT NAME':<26} {'CLASS / BATCH':<18} {'SCORE':<12} {'TOTAL TIME'}")
    print(f"{'═' * width}")
    
    if not entries:
        print(f"\n  {Colors.DIM}No scores registered yet. As students join at http://{get_lan_ip()}:{HUB_PORT}, their scores appear here live!{Colors.RESET}\n")
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


def public_web_sharing_guide():
    """Instructions and instant public tunnel helper for when participants lack common Wi-Fi."""
    clear_screen()
    print_banner("PUBLIC WEBSITE SHARING GUIDE", "No common Wi-Fi needed — participants connect over mobile data", badge="CLOUD / TUNNEL", color=Colors.BRIGHT_CYAN)
    
    guide_text = (
        f"{Colors.BOLD}OPTION 1: Free Cloud Hosting (Recommended for Big Workshops){Colors.RESET}\n"
        f"  Deploy this repository directly to Render (https://render.com) or Railway:\n"
        f"  1. Push this repo to your GitHub.\n"
        f"  2. On Render.com, click 'New Web Service' -> Connect your repo.\n"
        f"  3. Set Start Command: {Colors.BRIGHT_GREEN}python3 organizer.py --server-only{Colors.RESET}\n"
        f"  4. Done! Render provides a public URL: {Colors.BRIGHT_YELLOW}https://<your-project>.onrender.com{Colors.RESET}\n"
        f"     • Students open: {Colors.BRIGHT_YELLOW}https://<your-project>.onrender.com{Colors.RESET}\n"
        f"     • Organizer opens: {Colors.BRIGHT_CYAN}https://<your-project>.onrender.com/organizer.html{Colors.RESET}\n\n"
        f"{Colors.BOLD}OPTION 2: Instant Public Tunnel from your Laptop (Zero Sign-up){Colors.RESET}\n"
        f"  Run this single command in a new terminal tab while this hub is running:\n"
        f"  {Colors.BRIGHT_GREEN}ssh -R 80:localhost:{HUB_PORT} nokey@localhost.run{Colors.RESET}\n"
        f"  It will generate a live public HTTPS address (e.g. https://xyz.lhr.life) that anyone\n"
        f"  can open from their phone or laptop data connection!\n"
    )
    print_box(guide_text, title="HOSTING WITHOUT LOCAL WI-FI", color=Colors.BRIGHT_YELLOW)
    
    opts = [
        "Test / Launch instant SSH tunnel now (localhost.run)",
        "Back to Main Menu"
    ]
    c = ask_choice("Action:", opts)
    if c == 0:
        print(f"\n{Colors.BRIGHT_YELLOW}Starting public SSH tunnel on port {HUB_PORT}... Press Ctrl+C to stop tunnel.{Colors.RESET}\n")
        try:
            subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{HUB_PORT}", "nokey@localhost.run"])
        except Exception as e:
            print(f"Could not start tunnel: {e}")
        pause()


def organizer_reset_leaderboard():
    """Reset room leaderboard and speed bonuses."""
    clear_screen()
    print_banner("RESET LEADERBOARD & SPEED BONUSES", "Wipe scores and start a fresh tournament round", badge="DANGER ZONE", color=Colors.BRIGHT_RED)
    
    print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}WARNING:{Colors.RESET} This will wipe all participant scores, completion times, and first-finisher bonus claims.\n")
    confirm = ask_text("Type 'RESET' to confirm or press Enter to cancel")
    if confirm.strip() == "RESET":
        reset_leaderboard(clear_first_finishers=True)
        print(f"\n{Colors.BRIGHT_GREEN}✔ Leaderboard and bonus records successfully cleared!{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}Operation cancelled.{Colors.RESET}\n")
    pause()


def organizer_menu():
    """Main Organizer Dashboard."""
    ensure_hub_running()
    
    while True:
        clear_screen()
        print_banner(
            "FOSS MEC: ORGANIZER & FACILITATOR DASHBOARD",
            "Central Workshop Hub, Stage Controls & Master Leaderboard",
            badge="PRESENTER MODE",
            color=Colors.BRIGHT_YELLOW
        )
        print_hub_header()
        
        options = [
            "🔓 Stage Unlock Controller (Release Stage 2, 3, 4, 5 live to all laptops)",
            "🏆 Projector View: Live Room Leaderboard (Scores & Times)",
            "🔑 Project Stage Unlock Codes (Big Screen Display)",
            "🌐 Public Website Tunnel (Share via Mobile Data / No Common Wi-Fi)",
            "📽️  Projector View: Git Bingo (Clues & Answer Reveals)",
            "📽️  Projector View: Git Detective (Crime Scenes & Reveals)",
            "📋 Presenter Script: Branching & Merging Demo (4:10–4:40)",
            "🔑 Git Quest Token Verifier (Check Student Codes)",
            "📦 Generate Practice Sandbox Git Repository",
            "🗑️  Reset Room Leaderboard & Speed Bonuses"
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
            public_web_sharing_guide()
        elif choice == 4:
            projector_bingo()
        elif choice == 5:
            projector_detective()
        elif choice == 6:
            projector_demo_companion()
        elif choice == 7:
            token_verifier_tool()
        elif choice == 8:
            generate_sandbox_repo()
        elif choice == 9:
            organizer_reset_leaderboard()

if __name__ == "__main__":
    if "--server-only" in sys.argv:
        port = int(os.environ.get("PORT", 5000))
        server, actual_port = start_hub_server(port=port, start_beacon=False)
        print(f"🚀 FOSS MEC Workshop Central Hub running on http://0.0.0.0:{actual_port}")
        try:
            server.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            print("\nShutting down server.")
            server.server_close()
        sys.exit(0)

    try:
        organizer_menu()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Colors.RESET}Exited cleanly.")
