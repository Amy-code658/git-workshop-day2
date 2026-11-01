"""
showdown.py - Activity E: Final Showdown & Wrap-Up
Rapid-fire individual quiz with timer tracking and answer streaks.
"""

import os
import json
import time
from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    ask_choice, print_box
)
from engine.state import format_seconds

def load_showdown_questions():
    content_dir = os.path.join(os.path.dirname(__file__), "content")
    path = os.path.join(content_dir, "showdown_questions.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class FinalShowdownGame:
    def __init__(self, questions=None):
        self.questions = questions or load_showdown_questions()
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.correct_count = 0
        self.start_time = None
        self.elapsed_time = 0.0

    def play(self):
        clear_screen()
        print_banner("THE FINAL SHOWDOWN", "Rapid-fire review of Git mastery • Timer is running!", badge="ACTIVITY E", color=Colors.BRIGHT_MAGENTA)
        print(f"{Colors.WHITE}Welcome to the Grand Finale!{Colors.RESET}")
        print("10 rapid-fire questions testing speed and accuracy.")
        print("Your total time is tracked and affects your final workshop standing!\n")
        pause("Press Enter to START TIMER & begin...")

        self.start_time = time.time()

        for idx, q in enumerate(self.questions, 1):
            clear_screen()
            self.elapsed_time = round(time.time() - self.start_time, 1)
            badge = f"Q {idx}/{len(self.questions)}"
            streak_display = f"🔥 Streak: {self.streak}" if self.streak > 1 else ""
            status_line = f"Score: {self.score} pts | ⏱️ Time: {format_seconds(self.elapsed_time)} | {streak_display}"
            print_banner(f"FINAL SHOWDOWN", status_line, badge=badge, color=Colors.CYAN)
            
            chosen_idx = ask_choice(q["question"], q["options"], allow_quit=True)
            if chosen_idx == -1:
                self.elapsed_time = round(time.time() - self.start_time, 1)
                print(f"\n{Colors.YELLOW}Leaving Showdown. Score: {self.score} pts. Time: {format_seconds(self.elapsed_time)}{Colors.RESET}")
                pause()
                return self.score, self.elapsed_time, False

            if chosen_idx == q["correct_index"]:
                self.correct_count += 1
                self.streak += 1
                if self.streak > self.max_streak:
                    self.max_streak = self.streak
                
                multiplier = 1.0 + (self.streak - 1) * 0.2
                pts = int(10 * multiplier)
                self.score += pts
                print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ CORRECT! (+{pts} pts){Colors.RESET}")
            else:
                self.streak = 0
                correct_text = q["options"][q["correct_index"]]
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✘ INCORRECT! Correct: {correct_text}{Colors.RESET}")

            pause("Press Enter for the next question...")

        self.elapsed_time = round(time.time() - self.start_time, 1)
        clear_screen()
        print_banner("WORKSHOP WRAP-UP COMPLETE", f"Score: {self.score} pts | Time: {format_seconds(self.elapsed_time)}", badge="FINALE", color=Colors.GREEN)
        pause()
        return self.score, self.elapsed_time, True

def run_showdown():
    game = FinalShowdownGame()
    return game.play()
