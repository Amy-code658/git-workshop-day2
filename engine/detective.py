"""
detective.py - Activity B: Git Detective
Terminal scenario problem-solving cases with timer tracking and randomized case selection.
"""

import os
import json
import time
import random
from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    print_terminal_sim, print_box, ask_choice
)
from engine.state import format_seconds

def load_detective_cases(count=6):
    content_dir = os.path.join(os.path.dirname(__file__), "content")
    path = os.path.join(content_dir, "detective_cases.json")
    with open(path, "r", encoding="utf-8") as f:
        cases = json.load(f)
    return random.sample(cases, min(count, len(cases)))

class GitDetectiveGame:
    def __init__(self, cases=None, count=6):
        self.cases = cases or load_detective_cases(count=count)
        self.score = 0
        self.total_points = len(self.cases) * 20
        self.start_time = None
        self.elapsed_time = 0.0

    def play(self):
        clear_screen()
        print_banner("GIT DETECTIVE: TERMINAL MYSTERIES", "Analyze problem scenarios & identify the right fix", badge="ACTIVITY B")
        print(f"{Colors.WHITE}Welcome, Git Detective!{Colors.RESET}")
        print(f"You will investigate {len(self.cases)} randomized terminal crime scenes (conflicts, detached branches, etc.).")
        print("Your time is tracked! Solve the cases quickly for leaderboard ranking.\n")
        pause("Press Enter to START TIMER & begin the investigation...")

        self.start_time = time.time()

        for idx, case in enumerate(self.cases, 1):
            clear_screen()
            self.elapsed_time = round(time.time() - self.start_time, 1)
            badge = f"CASE {idx}/{len(self.cases)}"
            status_line = f"Score: {self.score}/{self.total_points} | ⏱️ Time: {format_seconds(self.elapsed_time)}"
            print_banner(f"{case['title'].upper()}", status_line, badge=badge, color=Colors.YELLOW)
            
            print_box(case["scenario"], title="CASE BRIEFING", color=Colors.CYAN)
            print_terminal_sim(case["command_sim"], case["output_sim"], title=f"EVIDENCE LOG - {case['title']}")
            
            chosen_idx = ask_choice(case["question"], case["options"], allow_quit=True)
            if chosen_idx == -1:
                self.elapsed_time = round(time.time() - self.start_time, 1)
                print(f"\n{Colors.YELLOW}Leaving investigation. Score: {self.score} pts. Time: {format_seconds(self.elapsed_time)}{Colors.RESET}")
                pause()
                return self.score, self.elapsed_time, False
                
            if chosen_idx == case["correct_index"]:
                self.score += 20
                print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ CASE SOLVED! (+20 Points){Colors.RESET}")
                print(f"{Colors.GREEN}{case['explanation']}{Colors.RESET}\n")
            else:
                correct_text = case["options"][case["correct_index"]]
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✘ INCORRECT DIAGNOSIS!{Colors.RESET}")
                print(f"{Colors.BOLD}Correct fix:{Colors.RESET} {Colors.GREEN}{correct_text}{Colors.RESET}\n")
                
            pause("Press Enter for the next case...")

        self.elapsed_time = round(time.time() - self.start_time, 1)
        clear_screen()
        print_banner("INVESTIGATION COMPLETE", f"Score: {self.score}/{self.total_points} | Time: {format_seconds(self.elapsed_time)}", badge="REPORT", color=Colors.GREEN)
        pause()
        return self.score, self.elapsed_time, True

def run_detective(count=6):
    game = GitDetectiveGame(count=count)
    return game.play()
