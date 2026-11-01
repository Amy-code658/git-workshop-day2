"""
showdown.py - Activity E: Final Showdown & Wrap-Up
Rapid-fire individual quiz reviewing essential Git & GitHub knowledge from Day 1 and Day 2.
"""

import os
import json
import time
from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    ask_choice, print_box
)

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

    def play(self):
        clear_screen()
        print_banner("THE FINAL SHOWDOWN", "Rapid-fire individual review of Git & GitHub mastery", badge="ACTIVITY E", color=Colors.BRIGHT_MAGENTA)
        print(f"{Colors.WHITE}Welcome to the Day 2 Grand Finale!{Colors.RESET}")
        print("Test your speed and memory across 10 rapid-fire questions.")
        print(f"Build answer streaks for bonus points!\n")
        pause("Press Enter when you are ready to start...")

        for idx, q in enumerate(self.questions, 1):
            clear_screen()
            badge = f"Q {idx}/{len(self.questions)}"
            streak_display = f"🔥 Streak: {self.streak} (x{1 + self.streak * 0.2:.1f})" if self.streak > 1 else ""
            print_banner(f"FINAL SHOWDOWN", f"Score: {self.score} pts | {streak_display}", badge=badge, color=Colors.CYAN)
            
            chosen_idx = ask_choice(q["question"], q["options"], allow_quit=True)
            if chosen_idx == -1:
                print(f"\n{Colors.YELLOW}Leaving Final Showdown. Final score: {self.score} pts.{Colors.RESET}")
                pause()
                return self.score

            if chosen_idx == q["correct_index"]:
                self.correct_count += 1
                self.streak += 1
                if self.streak > self.max_streak:
                    self.max_streak = self.streak
                
                # Base points + streak multiplier
                multiplier = 1.0 + (self.streak - 1) * 0.2
                pts = int(10 * multiplier)
                self.score += pts
                
                print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ CORRECT! (+{pts} pts){Colors.RESET}")
                print(f"{Colors.GREEN}{q['explanation']}{Colors.RESET}\n")
            else:
                self.streak = 0
                correct_text = q["options"][q["correct_index"]]
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✘ INCORRECT!{Colors.RESET}")
                print(f"Correct answer: {Colors.BOLD}{correct_text}{Colors.RESET}")
                print(f"{Colors.DIM}{q['explanation']}{Colors.RESET}\n")

            pause("Press Enter for the next question...")

        # Final Showdown ceremony
        clear_screen()
        total_q = len(self.questions)
        pct = (self.correct_count / total_q) * 100
        
        if pct >= 90:
            tier = "🏆 Git Grandmaster (Outstanding Performance!)"
        elif pct >= 70:
            tier = "⭐ Git Champion (Strong Foundation!)"
        else:
            tier = "🌱 Git Explorer (Great Progress!)"
            
        print_banner("WORKSHOP WRAP-UP COMPLETE", tier, badge="FINALE", color=Colors.GREEN)
        
        summary = (
            f"Questions Solved: {self.correct_count} / {total_q} ({pct:.0f}%)\n"
            f"Longest Streak:   {self.max_streak} in a row\n"
            f"Final Score:      {self.score} Points\n\n"
            f"NEXT STEPS:\n"
            f"• Keep making small daily commits on GitHub.\n"
            f"• Star and fork open-source projects.\n"
            f"• Practice branching on all your personal coding tasks!"
        )
        print_box(summary, title="DAY 2 ACHIEVEMENT REPORT", color=Colors.BRIGHT_CYAN)
        pause()
        return self.score

def run_showdown():
    game = FinalShowdownGame()
    return game.play()
