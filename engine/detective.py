"""
detective.py - Activity B: Git Detective
Terminal scenario problem-solving cases to identify what happened and select the correct remedy.
"""

import os
import json
from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    print_terminal_sim, print_box, ask_choice
)

def load_detective_cases():
    content_dir = os.path.join(os.path.dirname(__file__), "content")
    path = os.path.join(content_dir, "detective_cases.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class GitDetectiveGame:
    def __init__(self, cases=None):
        self.cases = cases or load_detective_cases()
        self.score = 0
        self.total_points = len(self.cases) * 20

    def play(self):
        clear_screen()
        print_banner("GIT DETECTIVE: TERMINAL MYSTERIES", "Analyze problem scenarios & identify the right fix", badge="ACTIVITY B")
        print(f"{Colors.WHITE}Welcome, Git Detective!{Colors.RESET}")
        print("Real-world developers run into Git output errors and puzzling states daily.")
        print("Your job: inspect the terminal output, diagnose the issue, and pick the exact right fix.\n")
        print(f"{Colors.DIM}Each solved case awards up to 20 detective points.{Colors.RESET}\n")
        pause("Press Enter to begin the investigation...")

        for idx, case in enumerate(self.cases, 1):
            clear_screen()
            badge = f"CASE {idx}/{len(self.cases)}"
            print_banner(f"{case['title'].upper()}", f"Difficulty: {case['difficulty']} | Points: {self.score}/{self.total_points}", badge=badge, color=Colors.YELLOW)
            
            # Scenario briefing
            print_box(case["scenario"], title="CASE BRIEFING", color=Colors.CYAN)
            
            # Simulated terminal output
            print_terminal_sim(case["command_sim"], case["output_sim"], title=f"EVIDENCE LOG - {case['title']}")
            
            # Question & choices
            chosen_idx = ask_choice(case["question"], case["options"], allow_quit=True)
            
            if chosen_idx == -1:
                print(f"\n{Colors.YELLOW}Leaving crime scene investigation. Final score: {self.score} pts.{Colors.RESET}")
                pause()
                return self.score
                
            correct_idx = case["correct_index"]
            if chosen_idx == correct_idx:
                self.score += 20
                print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ CASE SOLVED! (+20 Points){Colors.RESET}")
                print(f"{Colors.GREEN}{case['explanation']}{Colors.RESET}\n")
            else:
                chosen_text = case["options"][chosen_idx]
                correct_text = case["options"][correct_idx]
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✘ INCORRECT DIAGNOSIS!{Colors.RESET}")
                print(f"You selected: {chosen_text}")
                print(f"{Colors.BOLD}Correct fix:{Colors.RESET} {Colors.GREEN}{correct_text}{Colors.RESET}\n")
                print(f"{Colors.DIM}{case['explanation']}{Colors.RESET}\n")
                
            if "pro_tip" in case:
                print(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}💡 DETECTIVE PRO-TIP:{Colors.RESET} {case['pro_tip']}\n")
                
            pause("Press Enter for the next case...")

        # End of investigation summary
        clear_screen()
        pct = (self.score / self.total_points) * 100 if self.total_points > 0 else 0
        if pct >= 90:
            rank = "Master Git Inspector 🕵️‍♂️ (Top 5%)"
        elif pct >= 70:
            rank = "Senior Git Detective 🔍"
        else:
            rank = "Junior Sleuth in Training 📋"
            
        print_banner("INVESTIGATION COMPLETE", f"Rank: {rank}", badge="REPORT", color=Colors.GREEN)
        print(f"Total Score: {Colors.BOLD}{self.score} / {self.total_points} points ({pct:.0f}%){Colors.RESET}\n")
        print("You're now ready to troubleshoot everyday Git hiccups on your laptop!")
        pause()
        return self.score

def run_detective():
    game = GitDetectiveGame()
    return game.play()
