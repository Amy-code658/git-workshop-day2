"""
ui.py - Cross-platform terminal UI helper for Git Workshop Day 2 Games.
Zero external dependencies (pure Python standard library).
Compatible with Linux, macOS, and Windows (cmd, PowerShell, Git Bash).
"""

import os
import sys
import time
import textwrap

# Enable ANSI escape sequences on Windows if running in cmd/powershell
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# Determine if terminal supports colors
SUPPORTS_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
if os.environ.get("NO_COLOR"):
    SUPPORTS_COLOR = False

class Colors:
    if SUPPORTS_COLOR:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[2m"
        UNDERLINE = "\033[4m"
        
        # Standard colors
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"
        
        # Bright colors
        BRIGHT_RED = "\033[91m"
        BRIGHT_GREEN = "\033[92m"
        BRIGHT_YELLOW = "\033[93m"
        BRIGHT_BLUE = "\033[94m"
        BRIGHT_MAGENTA = "\033[95m"
        BRIGHT_CYAN = "\033[96m"
        BRIGHT_WHITE = "\033[97m"
        
        # Backgrounds
        BG_BLUE = "\033[44m"
        BG_GREEN = "\033[42m"
        BG_RED = "\033[41m"
        BG_MAGENTA = "\033[45m"
        BG_CYAN = "\033[46m"
        BG_GRAY = "\033[100m"
    else:
        RESET = ""
        BOLD = ""
        DIM = ""
        UNDERLINE = ""
        BLACK = ""
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        BRIGHT_RED = ""
        BRIGHT_GREEN = ""
        BRIGHT_YELLOW = ""
        BRIGHT_BLUE = ""
        BRIGHT_MAGENTA = ""
        BRIGHT_CYAN = ""
        BRIGHT_WHITE = ""
        BG_BLUE = ""
        BG_GREEN = ""
        BG_RED = ""
        BG_MAGENTA = ""
        BG_CYAN = ""
        BG_GRAY = ""


def get_terminal_width(default=78):
    """Return terminal width or safe default."""
    try:
        columns, _ = os.get_terminal_size()
        return max(50, min(columns, 100))
    except (OSError, ValueError):
        return default


def clear_screen():
    """Clear terminal safely across platforms."""
    if sys.platform == "win32":
        os.system("cls")
    else:
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.flush()


def pause(message="Press Enter to continue..."):
    """Prompt user to press Enter to continue."""
    print(f"\n{Colors.DIM}{message}{Colors.RESET}", end="")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print()


def print_banner(title, subtitle=None, badge=None, color=Colors.CYAN):
    """Print a top-level framed banner."""
    width = get_terminal_width()
    inner_width = width - 4
    
    print(f"\n{color}{Colors.BOLD}╔{'═' * (width - 2)}╗{Colors.RESET}")
    
    # Title line
    title_str = f" {title} "
    if badge:
        title_str += f"[{badge}] "
    print(f"{color}{Colors.BOLD}║{Colors.RESET} {Colors.BOLD}{title_str.center(inner_width)}{Colors.RESET} {color}{Colors.BOLD}║{Colors.RESET}")
    
    # Subtitle line
    if subtitle:
        sub_str = f" {subtitle} "
        print(f"{color}{Colors.BOLD}║{Colors.RESET} {Colors.DIM}{sub_str.center(inner_width)}{Colors.RESET} {color}{Colors.BOLD}║{Colors.RESET}")
        
    print(f"{color}{Colors.BOLD}╚{'═' * (width - 2)}╝{Colors.RESET}\n")


def print_box(text, title=None, color=Colors.BLUE, bg=None):
    """Print text wrapped inside a border box."""
    width = get_terminal_width()
    inner_width = width - 4
    lines = []
    
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
        else:
            lines.extend(textwrap.wrap(paragraph, width=inner_width))
            
    header = f"─ {title} " if title else ""
    header_bar = header + "─" * (width - 2 - len(header))
    
    print(f"{color}┌{header_bar}┐{Colors.RESET}")
    for line in lines:
        padded = line.ljust(inner_width)
        print(f"{color}│{Colors.RESET} {padded} {color}│{Colors.RESET}")
    print(f"{color}└{'─' * (width - 2)}┘{Colors.RESET}")


def print_terminal_sim(command, output, title="TERMINAL OUTPUT"):
    """Render a simulated terminal window with prompt and output."""
    width = get_terminal_width()
    inner_width = width - 4
    
    print(f"\n{Colors.BRIGHT_WHITE}{Colors.BG_GRAY} [● ● ●] {title.ljust(inner_width - 8)} {Colors.RESET}")
    print(f"{Colors.DIM}┌{'─' * (width - 2)}┐{Colors.RESET}")
    
    # Render command prompt
    prompt_str = f"$ {command}"
    print(f"{Colors.DIM}│{Colors.RESET} {Colors.BRIGHT_GREEN}{Colors.BOLD}{prompt_str.ljust(inner_width)}{Colors.RESET} {Colors.DIM}│{Colors.RESET}")
    print(f"{Colors.DIM}├{'─' * (width - 2)}┤{Colors.RESET}")
    
    # Render output lines
    for line in output.split("\n"):
        # Wrap long lines if necessary
        wrapped = textwrap.wrap(line, width=inner_width) or [""]
        for w in wrapped:
            print(f"{Colors.DIM}│{Colors.RESET} {Colors.WHITE}{w.ljust(inner_width)}{Colors.RESET} {Colors.DIM}│{Colors.RESET}")
            
    print(f"{Colors.DIM}└{'─' * (width - 2)}┘{Colors.RESET}\n")


def ask_choice(prompt_text, options, allow_quit=True):
    """
    Present a numbered list of options and prompt user for selection.
    Returns 0-based index or -1 if quit.
    """
    width = get_terminal_width()
    print(f"\n{Colors.BOLD}{prompt_text}{Colors.RESET}\n")
    
    for i, opt in enumerate(options, 1):
        print(f"  {Colors.BRIGHT_CYAN}{Colors.BOLD}[{i}]{Colors.RESET} {opt}")
        
    if allow_quit:
        print(f"  {Colors.DIM}[q] Return to menu / Quit{Colors.RESET}")
        
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}Enter your choice: {Colors.RESET}").strip()
            if allow_quit and choice.lower() in ("q", "quit", "exit"):
                return -1
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
            print(f"{Colors.RED}Please enter a number between 1 and {len(options)}.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a valid number.{Colors.RESET}")
        except (EOFError, KeyboardInterrupt):
            print()
            return -1


def ask_text(prompt_text, default=None):
    """Ask user for text input."""
    hint = f" [{default}]" if default else ""
    try:
        val = input(f"{Colors.YELLOW}{prompt_text}{hint}: {Colors.RESET}").strip()
        if not val and default:
            return default
        return val
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def status_badge(passed, label=None):
    """Return colored pass/fail badge."""
    if passed:
        lbl = label or "PASS"
        return f"{Colors.BRIGHT_GREEN}{Colors.BOLD}[✔ {lbl}]{Colors.RESET}"
    else:
        lbl = label or "PENDING"
        return f"{Colors.BRIGHT_RED}{Colors.BOLD}[✘ {lbl}]{Colors.RESET}"
