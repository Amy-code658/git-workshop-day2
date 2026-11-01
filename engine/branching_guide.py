"""
branching_guide.py - Activity C: Branching & Merging Interactive Guide
Guides students through the live 6-step branching, committing, pushing, and PR workflow.
"""

from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    print_box, print_terminal_sim
)

STEPS = [
    {
        "step": 1,
        "title": "Create & Switch to a New Branch",
        "command": "git switch -c add-my-section",
        "description": "Never work directly on the 'main' branch when proposing new features. Create an isolated branch.",
        "sim_output": "Switched to a new branch 'add-my-section'",
        "tip": "The '-c' flag stands for 'create'. In older Git tutorials, you might see 'git checkout -b <name>'."
    },
    {
        "step": 2,
        "title": "Make Your Edits in README.md",
        "command": "echo \"## Contributed by My Name\" >> README.md",
        "description": "Open README.md in VS Code, Notepad, or your favorite editor and add a new section or short bio.",
        "sim_output": "(File updated on disk. Check with 'git status'!)",
        "tip": "Running 'git status' right now will show 'modified: README.md' highlighted in red."
    },
    {
        "step": 3,
        "title": "Stage and Commit the Change",
        "command": "git add . && git commit -m \"Add my section to README\"",
        "description": "Stage your updated README.md and save a permanent snapshot with a meaningful commit message.",
        "sim_output": "[add-my-section 7b8e1f2] Add my section to README\n 1 file changed, 2 insertions(+)",
        "tip": "Commits on this branch stay isolated from main until merged."
    },
    {
        "step": 4,
        "title": "Push the Branch to GitHub",
        "command": "git push -u origin add-my-section",
        "description": "Upload your local branch to your GitHub repository so you can open a pull request.",
        "sim_output": "Enumerating objects: 5, done.\nTotal 3 (delta 1), reused 0 (delta 0)\nTo https://github.com/USER/repo.git\n * [new branch]      add-my-section -> add-my-section\nBranch 'add-my-section' set up to track remote branch 'add-my-section' from 'origin'.",
        "tip": "The '-u' flag tells Git to remember this remote branch for future 'git push' and 'git pull' calls."
    },
    {
        "step": 5,
        "title": "Open GitHub and Create a Pull Request (PR)",
        "command": "Open browser -> Navigate to your GitHub repo -> Click 'Compare & pull request'",
        "description": "GitHub will display a bright yellow banner alerting you that 'add-my-section had recent pushes'. Click 'Compare & pull request', add a friendly description, and click 'Create pull request'.",
        "sim_output": "Pull Request #1 opened: 'Add my section to README'",
        "tip": "A Pull Request doesn't merge immediately—it opens a discussion space for reviews, questions, and automated checks."
    },
    {
        "step": 6,
        "title": "Review the Diff and Merge into Main",
        "command": "Click 'Files changed' -> Inspect additions -> Click 'Merge pull request' -> 'Confirm merge'",
        "description": "Inspect the green (+) lines showing your additions. Once satisfied, click 'Merge pull request'. Then switch back locally to main ('git switch main') and run 'git pull' to sync the merged changes!",
        "sim_output": "Pull request successfully merged and closed.\nLocal sync: $ git switch main && git pull",
        "tip": "Congratulations! You just completed the industry-standard branch-commit-push-PR-merge workflow!"
    }
]

def run_branching_guide():
    clear_screen()
    print_banner("BRANCHING & MERGING COMPANION", "Step-by-step collaborative Git workflow", badge="ACTIVITY C", color=Colors.BRIGHT_BLUE)
    print("This guide walks you through the 6 core steps demonstrated by the facilitator.\n")
    pause("Press Enter to begin Step 1...")

    for item in STEPS:
        clear_screen()
        badge = f"STEP {item['step']} OF 6"
        print_banner(item["title"].upper(), f"Activity C: Branching & Merging", badge=badge, color=Colors.CYAN)
        
        info = (
            f"{item['description']}\n\n"
            f"COMMAND TO RUN IN TERMINAL:\n"
            f"  {Colors.BOLD}{Colors.BRIGHT_GREEN}{item['command']}{Colors.RESET}\n\n"
            f"PRO TIP: {item['tip']}"
        )
        print_box(info, title=f"ACTION FOR STEP {item['step']}", color=Colors.YELLOW)
        
        print_terminal_sim(item["command"], item["sim_output"], title="EXPECTED OUTPUT")
        
        pause(f"Press Enter when you have completed Step {item['step']}...")

    clear_screen()
    print_banner("COLLABORATIVE WORKFLOW COMPLETE!", "You're ready for the Git Quest challenge!", badge="DONE", color=Colors.GREEN)
    print("Now run option [4] Git Quest to verify your progress and earn your 100 points!\n")
    pause()
