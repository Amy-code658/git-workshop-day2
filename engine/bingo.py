"""
bingo.py - Activity A: Git Bingo (Laptop Edition)
Interactive 3x3 terminal Bingo board matching Git concepts and commands.
"""

import os
import json
import random
from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    get_terminal_width, ask_choice, ask_text
)

def load_bingo_items():
    content_dir = os.path.join(os.path.dirname(__file__), "content")
    path = os.path.join(content_dir, "bingo_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class BingoGame:
    def __init__(self, items=None):
        raw_items = items or load_bingo_items()
        # Pick 9 items for a 3x3 grid
        random.seed()
        self.grid_items = random.sample(raw_items, min(9, len(raw_items)))
        self.marked = [False] * len(self.grid_items)
        self.score = 0
        self.bingo_awarded = False
        self.question_pool = list(self.grid_items)
        random.shuffle(self.question_pool)

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
        bingo_count = 0
        for line in lines:
            if all(self.marked[i] for i in line):
                bingo_count += 1
        return bingo_count

    def render_board(self):
        """Draw 3x3 Bingo grid in terminal."""
        width = min(get_terminal_width(), 76)
        col_w = (width - 4) // 3
        
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}┌─ YOUR 3x3 GIT BINGO CARD {'─' * (width - 29)}┐{Colors.RESET}")
        
        for row in range(3):
            # Print row contents
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
                
                # Visual padding
                visible_len = 4 + len(cmd_text[:col_w - 5])
                pad = max(0, col_w - visible_len)
                row_cells.append(cell_str + " " * pad)
                
            print(f"{Colors.BRIGHT_CYAN}│{Colors.RESET} " + f" {Colors.DIM}│{Colors.RESET} ".join(row_cells) + f" {Colors.BRIGHT_CYAN}│{Colors.RESET}")
            
            if row < 2:
                print(f"{Colors.BRIGHT_CYAN}├{'─' * (width - 2)}┤{Colors.RESET}")
                
        print(f"{Colors.BRIGHT_CYAN}└{'─' * (width - 2)}┘{Colors.RESET}")
        
        # Status footer
        marked_count = sum(self.marked)
        bingos = self.check_bingo()
        print(f"  {Colors.BOLD}Marked:{Colors.RESET} {marked_count}/9   {Colors.BOLD}Score:{Colors.RESET} {self.score} pts   {Colors.BOLD}Bingos:{Colors.RESET} {bingos}")

    def play(self):
        """Run the interactive student Bingo game."""
        clear_screen()
        print_banner("GIT BINGO - LAPTOP EDITION", "Match the Git concept to the command on your card", badge="ACTIVITY A")
        print(f"{Colors.WHITE}Welcome to Git Bingo!{Colors.RESET}")
        print("Read each clue, inspect your 3x3 board, and select the square (1-9) that has the right command.")
        print("Complete rows, columns, or diagonals for bonus BINGO points!\n")
        pause()

        round_num = 1
        for current_item in self.question_pool:
            clear_screen()
            print_banner(f"GIT BINGO: ROUND {round_num} OF {len(self.question_pool)}", f"Score: {self.score} points", badge="BINGO")
            self.render_board()
            
            # Find the winning index on the board
            target_idx = self.grid_items.index(current_item)
            
            print(f"\n{Colors.BRIGHT_YELLOW}{Colors.BOLD}CLUE:{Colors.RESET} {Colors.BRIGHT_WHITE}{current_item['prompt']}{Colors.RESET}\n")
            
            # Ask student to pick square
            while True:
                user_input = ask_text("Select square number (1-9) or [q] to exit")
                if user_input.lower() in ("q", "quit", "exit"):
                    print(f"\n{Colors.YELLOW}Leaving Git Bingo. Final score: {self.score} pts.{Colors.RESET}")
                    pause()
                    return self.score
                try:
                    chosen_idx = int(user_input) - 1
                    if 0 <= chosen_idx < 9:
                        break
                    print(f"{Colors.RED}Please pick a number between 1 and 9.{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Please enter a valid number (1-9).{Colors.RESET}")
            
            # Check answer
            if chosen_idx == target_idx:
                self.marked[target_idx] = True
                self.score += 20
                print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}✔ CORRECT!{Colors.RESET} {Colors.GREEN}Marked square [{target_idx + 1}] for '{current_item['command']}'. (+20 pts){Colors.RESET}")
                print(f"{Colors.DIM}{current_item['explanation']}{Colors.RESET}")
                
                # Check for new Bingo
                new_bingos = self.check_bingo()
                if new_bingos > 0 and not self.bingo_awarded:
                    self.score += 50
                    self.bingo_awarded = True
                    print(f"\n{Colors.BRIGHT_MAGENTA}{Colors.BOLD}🎉🎉🎉 BINGO! You connected 3 in a line! (+50 BONUS POINTS) 🎉🎉🎉{Colors.RESET}")
            else:
                chosen_cmd = self.grid_items[chosen_idx]["command"]
                correct_cmd = current_item["command"]
                print(f"\n{Colors.BRIGHT_RED}{Colors.BOLD}✘ NOT QUITE!{Colors.RESET} You picked [{chosen_idx + 1}] '{chosen_cmd}'.")
                print(f"The correct command for this clue was {Colors.BOLD}'{correct_cmd}'{Colors.RESET} on square [{target_idx + 1}].")
                print(f"{Colors.DIM}{current_item['explanation']}{Colors.RESET}")
                
            round_num += 1
            pause("Press Enter for the next clue...")
            
        # End game summary
        clear_screen()
        print_banner("GIT BINGO COMPLETED!", f"Final Score: {self.score} pts", badge="FINISH", color=Colors.GREEN)
        self.render_board()
        print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}Great job completing the Git Bingo round!{Colors.RESET}\n")
        pause()
        return self.score


def run_bingo():
    game = BingoGame()
    return game.play()
