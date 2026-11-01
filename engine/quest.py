"""
quest.py - Activity D: Git Quest (Individual 100-Point Challenge)
Automated non-destructive validator that inspects a student's real local Git repository
against the official Day 2 Checklist, computes their score, and issues a verification code.
"""

import os
import sys
import subprocess
import hashlib
from engine.ui import (
    Colors, clear_screen, pause, print_banner,
    print_box, ask_text, ask_choice, status_badge
)

def run_git_cmd(repo_dir, args):
    """Run a non-destructive git command in target repo directory."""
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=8
        )
        return proc.returncode == 0, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def generate_verification_token(name, score, task_flags):
    """Generate a tamper-evident verification token for facilitators."""
    flag_str = "".join("1" if f else "0" for f in task_flags)
    raw = f"{name.strip().lower()}:{score}:{flag_str}:gitworkshop2026"
    checksum = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:4].upper()
    clean_name = "".join(c for c in name if c.isalnum())[:8] or "STUDENT"
    return f"GQ-{score}-{clean_name}-{checksum}"


def verify_token(token):
    """Decode and verify a token."""
    parts = token.strip().upper().split("-")
    if len(parts) != 4 or parts[0] != "GQ":
        return False, "Invalid token format. Must look like 'GQ-100-NAME-XXXX'."
    
    try:
        score = int(parts[1])
        name = parts[2]
        provided_checksum = parts[3]
        
        # Test against plausible flag combinations matching the score
        # Full score check
        for flag_str in ("1111111", "1111110", "1111100", "1111000", "1110000"):
            raw = f"{name.lower()}:{score}:{flag_str}:gitworkshop2026"
            calc = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:4].upper()
            if calc == provided_checksum:
                return True, f"Valid Token! Participant: {name} | Score: {score}/100"
                
        return False, f"Checksum verification failed for token {token}."
    except Exception as e:
        return False, f"Error decoding token: {str(e)}"


class GitQuestValidator:
    def __init__(self, repo_path=None, student_name=None):
        self.repo_path = repo_path or os.getcwd()
        self.student_name = student_name or "Participant"
        self.results = []
        self.total_score = 0

    def evaluate(self):
        """Evaluate repository against the 7 action plan tasks."""
        self.results = []
        self.total_score = 0
        task_flags = [False] * 7

        # 1. Check repository status (10 pts)
        is_git, out, _ = run_git_cmd(self.repo_path, ["rev-parse", "--is-inside-work-tree"])
        t1_pass = (is_git and out.lower() == "true")
        if t1_pass:
            self.total_score += 10
            task_flags[0] = True
            msg = "Valid Git repository detected and status inspected."
        else:
            msg = "Not a Git repository. Run 'git init' or pass the correct folder."
        self.results.append({
            "num": 1,
            "title": "Check repository status",
            "points": 10,
            "awarded": 10 if t1_pass else 0,
            "passed": t1_pass,
            "details": msg
        })

        if not t1_pass:
            # Cannot check remaining local git tasks if not a git repo
            for i in range(2, 8):
                pts = [10, 10, 15, 15, 20, 20][i - 2]
                self.results.append({
                    "num": i,
                    "title": ["Create a branch", "Edit a file", "Stage and commit", "Push the branch", "Open a pull request", "Review the change"][i - 2],
                    "points": pts,
                    "awarded": 0,
                    "passed": False,
                    "details": "Requires a valid initialized Git repository."
                })
            return task_flags

        # 2. Create a branch (10 pts)
        # Check if there is more than 1 branch or current branch is not main/master
        ok, branches_out, _ = run_git_cmd(self.repo_path, ["branch", "--list"])
        branches = [b.replace("*", "").strip() for b in branches_out.split("\n") if b.strip()]
        has_custom_branch = any(b not in ("main", "master") for b in branches)
        ok_curr, curr_branch, _ = run_git_cmd(self.repo_path, ["branch", "--show-current"])
        
        t2_pass = has_custom_branch or (curr_branch not in ("main", "master") and curr_branch != "")
        if t2_pass:
            self.total_score += 10
            task_flags[1] = True
            active_info = f"Active branch: '{curr_branch}', Total branches: {len(branches)}"
        else:
            active_info = f"Only default branch found. Run 'git switch -c <branch-name>'."
        self.results.append({
            "num": 2,
            "title": "Create a branch",
            "points": 10,
            "awarded": 10 if t2_pass else 0,
            "passed": t2_pass,
            "details": active_info
        })

        # 3. Edit a file (10 pts)
        # Check if README.md exists and has content or commit history
        readme_path = None
        for cand in ["README.md", "readme.md", "README"]:
            p = os.path.join(self.repo_path, cand)
            if os.path.exists(p):
                readme_path = p
                break
                
        t3_pass = False
        if readme_path and os.path.getsize(readme_path) > 0:
            t3_pass = True
            t3_msg = f"Found '{os.path.basename(readme_path)}' ({os.path.getsize(readme_path)} bytes)."
        else:
            # Check if any tracked files exist
            ok, ls_out, _ = run_git_cmd(self.repo_path, ["ls-files"])
            if ls_out.strip():
                t3_pass = True
                t3_msg = f"Project files tracked: {len(ls_out.splitlines())} file(s)."
            else:
                t3_msg = "README.md not found or empty. Create or edit README.md."
                
        if t3_pass:
            self.total_score += 10
            task_flags[2] = True
            
        self.results.append({
            "num": 3,
            "title": "Edit a file (README.md)",
            "points": 10,
            "awarded": 10 if t3_pass else 0,
            "passed": t3_pass,
            "details": t3_msg
        })

        # 4. Stage and commit (15 pts)
        ok, log_out, _ = run_git_cmd(self.repo_path, ["log", "-n", "3", "--oneline"])
        commits = [c for c in log_out.split("\n") if c.strip()]
        t4_pass = len(commits) > 0
        if t4_pass:
            self.total_score += 15
            task_flags[3] = True
            t4_msg = f"Found commit(s). Latest: '{commits[0]}'"
        else:
            t4_msg = "No commits found in log. Run 'git add .' and 'git commit -m \"...\"'."
            
        self.results.append({
            "num": 4,
            "title": "Stage and commit",
            "points": 15,
            "awarded": 15 if t4_pass else 0,
            "passed": t4_pass,
            "details": t4_msg
        })

        # 5. Push the branch (15 pts)
        ok, remotes_out, _ = run_git_cmd(self.repo_path, ["remote", "-v"])
        has_remote = bool(remotes_out.strip())
        ok, rbranch_out, _ = run_git_cmd(self.repo_path, ["branch", "-r"])
        has_remote_branches = bool(rbranch_out.strip())
        
        t5_pass = has_remote and has_remote_branches
        if t5_pass:
            self.total_score += 15
            task_flags[4] = True
            t5_msg = f"Remote configured & pushed branch verified ({len(rbranch_out.splitlines())} remote ref(s))."
        elif has_remote:
            # Remote configured but maybe not yet pushed or offline fallback
            self.total_score += 10
            task_flags[4] = True
            t5_msg = f"Remote configured ('origin' exists). Run 'git push -u origin <branch>' to push."
        else:
            t5_msg = "No remote configured. Link to GitHub with 'git remote add origin <URL>'."
            
        self.results.append({
            "num": 5,
            "title": "Push the branch to GitHub",
            "points": 15,
            "awarded": 15 if t5_pass else (10 if has_remote else 0),
            "passed": t5_pass or has_remote,
            "details": t5_msg
        })

        # 6. Open a pull request (20 pts)
        # Interactive confirmation / verification
        print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}--- Interactive Verification (Tasks 6 & 7) ---{Colors.RESET}")
        pr_ans = ask_choice("Did you create a Pull Request on GitHub for your branch?", ["Yes, PR opened on GitHub", "Not yet / Skip"], allow_quit=False)
        t6_pass = (pr_ans == 0)
        if t6_pass:
            self.total_score += 20
            task_flags[5] = True
            t6_msg = "Pull Request confirmed."
        else:
            t6_msg = "Pull request not yet opened on GitHub."
            
        self.results.append({
            "num": 6,
            "title": "Open a pull request",
            "points": 20,
            "awarded": 20 if t6_pass else 0,
            "passed": t6_pass,
            "details": t6_msg
        })

        # 7. Review the change & merge (20 pts)
        merge_ans = ask_choice("Did you review and/or merge the Pull Request?", ["Yes, PR reviewed / merged", "Not yet / Skip"], allow_quit=False)
        t7_pass = (merge_ans == 0)
        if t7_pass:
            self.total_score += 20
            task_flags[6] = True
            t7_msg = "Pull Request review / merge completed."
        else:
            t7_msg = "Review & merge step pending."
            
        self.results.append({
            "num": 7,
            "title": "Review the change",
            "points": 20,
            "awarded": 20 if t7_pass else 0,
            "passed": t7_pass,
            "details": t7_msg
        })

        return task_flags


def run_quest():
    clear_screen()
    print_banner("GIT QUEST: 100-POINT INDIVIDUAL CHALLENGE", "Automated repository verification & checklist grader", badge="ACTIVITY D")
    print("This tool inspects your local Git practice repository against the Day 2 rubric.")
    print("Everything is checked locally on your laptop without modifying any files.\n")
    
    student_name = ask_text("Enter your name or handle", default="Participant")
    
    # Select target repository
    default_dir = os.getcwd()
    repo_input = ask_text(f"Path to your practice repository folder", default=default_dir)
    target_repo = os.path.abspath(os.path.expanduser(repo_input))
    
    if not os.path.isdir(target_repo):
        print(f"\n{Colors.RED}Directory not found: {target_repo}{Colors.RESET}")
        pause()
        return 0

    validator = GitQuestValidator(repo_path=target_repo, student_name=student_name)
    task_flags = validator.evaluate()
    
    clear_screen()
    print_banner(f"GIT QUEST SCORECARD: {student_name.upper()}", f"Inspected: {target_repo}", badge=f"{validator.total_score}/100 PTS")
    
    print(f"{'#':<3} {'TASK':<28} {'STATUS':<15} {'SCORE':<10} {'DETAILS'}")
    print(f"{'─' * 78}")
    
    for r in validator.results:
        badge = status_badge(r["passed"], f"{r['awarded']}/{r['points']}")
        print(f"{r['num']:<3} {r['title'][:26]:<28} {badge:<22} {r['details']}")
        
    print(f"{'─' * 78}")
    print(f"\n{Colors.BOLD}FINAL SCORE: {Colors.BRIGHT_GREEN}{validator.total_score} / 100 POINTS{Colors.RESET}")
    
    # Generate verification token
    token = generate_verification_token(student_name, validator.total_score, task_flags)
    
    token_box = (
        f"PARTICIPANT: {student_name}\n"
        f"SCORE: {validator.total_score} / 100\n"
        f"OFFICIAL VERIFICATION CODE: {token}\n\n"
        f"Show this code to the facilitator or enter it into the organizer dashboard."
    )
    print_box(token_box, title="OFFICIAL COMPLETION CERTIFICATE", color=Colors.BRIGHT_MAGENTA)
    
    pause()
    return validator.total_score
