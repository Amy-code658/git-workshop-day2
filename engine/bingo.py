"""
bingo.py - Activity A: Git Bingo (Laptop Edition)
Individual randomized 3x3 Bingo cards.
Stops immediately upon getting a BINGO (does not wait for all questions).
Measures time taken and awards first-finisher speed bonuses.
"""

import os
import json
import time
import random
from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    get_terminal_width, ask_choice, ask_text
)
from engine.state import format_seconds

def load_bingo_items():
    content_dir = os.path.join(os.path.dirname(__file__), "content")
    path = os.path.join(content_dir, "bingo_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class BingoGame:
    def __init__(self, items=None):
        raw_items = items or load_bingo_items()
        self.master_pool = list(raw_items)
        
        # Give every player a uniquely randomized 3x3 card
        random.seed()
        self.grid_items = random.sample(raw_items, min(9, len(raw_items)))
        self.marked = [False] * len(self.grid_items)
        self.score = 0
        self.start_time = None
        self.elapsed_time = 0.0

        # Master clue order
        self.clues = list(self.master_pool)
        random.shuffle(self.clues)

    def check_bingo(self):
        """Check for 3 in a row, column, or diagonal."""
        lines = [
            # Rows
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            # Columns
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            # Diagonals
            [0, 4, 8], [2, 4, 6]
        ]
        for line in lines:
            if all(self.marked[i] for i in line):
                return True
        return False

    def render_board(self):
        """Draw randomized 3x3 Bingo grid with live timer."""
        width = min(get_terminal_width(), 76)
        col_w = (width - 4) // 3
        
        current_elapsed = time.time() - self.start_time if self.start_time else 0.0
        time_str = format_seconds(current_elapsed)
        
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}┌─ YOUR 3x3 GIT BINGO CARD ─── ⏱️ TIME: {time_str} {'─' * (width - 48)}┐{Colors.RESET}")
        
        for row in range(3):
            row_cells = []
            for col in range(3):
                idx = row * 3 + col
                item = self.grid_items[idx]
                is_marked = self.marked[idx]
                
                cmd_text = item["command"]
                if is_marked:
                    cell_str = f"{Colors.BRIGHT_GREEN}{Colors.BOLD}[✔] {cmd_text[:col_w - 5]}{Colors.RESET}"
                else:
                    cell_str = f"{Colors.YELLOW}[{idx + 1}]{Colors.RESET} {Colors.WHITE}{cmd_text[:col_w - 5]}{Colors.RESET}"
                
                visible_len = 4 + len(cmd_text[:col_w - 5])
                pad = max(0, col_w - visible_len)
                row_cells.append(cell_str + " " * pad)
                
            print(f"{Colors.BRIGHT_CYAN}│{Colors.RESET} " + f" {Colors.DIM}│{Colors.RESET} ".join(row_cells) + f" {Colors.BRIGHT_CYAN}│{Colors.RESET}")
            if row < 2:
                print(f"{Colors.BRIGHT_CYAN}├{'─' * (width - 2)}┤{Colors.RESET}")
                
        print(f"{Colors.BRIGHT_CYAN}└{'─' * (width - 2)}┘{Colors.RESET}")
        marked_count = sum(self.marked)
        print(f"  {Colors.BOLD}Marked:{Colors.RESET} {marked_count}/9   {Colors.BOLD}Score:{Colors.RESET} {self.score} pts   {Colors.BOLD}Time:{Colors.RESET} {time_str}")

    def play(self):
        """Run interactive Bingo with live timing and instant stop on win."""
        clear_screen()
        print_banner("GIT BINGO - LAPTOP EDITION", "Random card per player • Race to complete 3 in a line!", badge="ACTIVITY A")
        print(f"{Colors.WHITE}Rules of Git Bingo:{Colors.RESET}")
        print("• Each player receives a unique 3x3 Bingo Card.")
        print("• Clues will be called one by one from the master pool.")
        print("• If the matching command is on your card, select its square (1-9).")
        print("• If it is NOT on your card, type [n] for the next clue.")
        print(f"• {Colors.BOLD}CRITICAL:{Colors.RESET} As soon as you get 3-in-a-row (row, column, or diagonal), the game stops immediately!")
        print(f"• Fastest finishers earn bonus points on the leaderboard.\n")
        pause("Press Enter to START TIMER & begin...")

        self.start_time = time.time()
        round_num = 1
        
        for current_clue in self.clues:
            clear_screen()
            self.elapsed_time = round(time.time() - self.start_time, 1)
            badge_info = f"Score: {self.score} pts | Time: {format_seconds(self.elapsed_time)}"
            print_banner(f"GIT BINGO: CALL #{round_num}", badge_info, badge="BINGO ROUND", color=Colors.CYAN)
            
            self.render_board()
            
            # Check if this clue's command is anywhere on the player's card
            card_commands = [item["command"] for item in self.grid_items]
            has_command_on_card = current_clue["command"] in card_commands
            target_idx = card_commands.index(current_clue["command"]) if has_command_on_card else -1
            
            print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}CALL #{round_num}:{Colors.RESET} {Colors.BRIGHT_WHITE}{current_clue['prompt']}{Colors.RESET}\n")
            print(f"{Colors.DIM}(Select square 1-9 to mark, [n] if not on your card, or [q] to exit){Colors.RESET}")
            
            while True:
                user_input = ask_text("Your action").strip().lower()
                if user_input in ("q", "quit", "exit"):
                    self.elapsed_time = round(time.time() - self.start_time, 1)
                    print(f"\n{Colors.YELLOW}Leaving Git Bingo. Final score: {self.score} pts. Time: {format_seconds(self.elapsed_time)}{Colors.RESET}")
                    pause()
                    return self.score, self.elapsed_time, False
                    
                if user_input in ("n", "next", "pass"):
                    if has_command_on_card and not self.marked[target_idx]:
                        print(f"{Colors.YELLOW}Notice: '{current_clue['command']}' was actually on square [{target_idx + 1}] on your card! Moving to next clue...{Colors.RESET}")
                    else:
                        print(f"{Colors.DIM}Next clue called...{Colors.RESET}")
                    break
                    
                try:
                    chosen_idx = int(user_input) - 1
                    if 0 <= chosen_idx < 9:
                        # Process square selection
                        if chosen_idx == target_idx:
                            self.marked[target_idx] = True
                            self.score += 20
                            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ CORRECT!{Colors.RESET} {Colors.GREEN}Marked square [{target_idx + 1}] for '{current_clue['command']}'. (+20 pts){Colors.RESET}")
                            
                            # CHECK FOR BINGO IMMEDIATELY! STOP GAME IF WON!
                            if self.check_bingo():
                                self.score += 50
                                self.elapsed_time = round(time.time() - self.start_time, 1)
                                
                                clear_screen()
                                print_banner("🎉🎉🎉 BINGO ACHIEVED! 🎉🎉🎉", f"Completed in {format_seconds(self.elapsed_time)} ({self.elapsed_time}s)!", badge="WINNER", color=Colors.BRIGHT_GREEN)
                                self.render_board()
                                print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}You completed 3 in a line! The Bingo round ends immediately! (+50 BONUS PTS){Colors.RESET}")
                                print(f"Final Score: {Colors.BOLD}{self.score} points{Colors.RESET} | Time: {Colors.BOLD}{format_seconds(self.elapsed_time)}{Colors.RESET}\n")
                                pause("Press Enter to return to main arena...")
                                return self.score, self.elapsed_time, True
                        else:
                            chosen_cmd = self.grid_items[chosen_idx]["command"]
                            print(f"\n{Colors.BRIGHT_RED}✘ '{chosen_cmd}' on square [{chosen_idx + 1}] does not match this clue!{Colors.RESET}")
                        break
                    print(f"{Colors.RED}Please pick a valid square (1-9) or enter 'n'.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Invalid input. Enter 1-9, 'n' (next), or 'q' (quit).{Colors.RESET}")
            
            round_num += 1
            pause("Press Enter for the next call...")

        self.elapsed_time = round(time.time() - self.start_time, 1)
        clear_screen()
        print_banner("GIT BINGO COMPLETED", f"Time: {format_seconds(self.elapsed_time)} | Score: {self.score} pts", badge="FINISH", color=Colors.GREEN)
        self.render_board()
        pause()
        return self.score, self.elapsed_time, False


def run_bingo():
    game = BingoGame()
    score, elapsed, won = game.play()
    return score, elapsed, won
