"""
state.py - Profile, Live Leaderboard, and Stage Lock Management.
Zero external dependencies (pure Python standard library).
"""

import os
import json
import time
import urllib.request
import urllib.error

SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".player_save.json")
LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leaderboard.json")

# Stage Unlock Keys (known to organizer; broadcast or announced when each round begins)
STAGE_PASSWORDS = {
    2: "DETECTIVE26",
    3: "BRANCH26",
    4: "QUEST26",
    5: "SHOWDOWN26"
}

STAGE_NAMES = {
    1: "Git Bingo",
    2: "Git Detective",
    3: "Branching Demo",
    4: "Git Quest (100 pts)",
    5: "Final Showdown"
}

class PlayerState:
    def __init__(self, name="", class_name="", organizer_url=None):
        self.name = name
        self.class_name = class_name
        self.score = 0
        self.unlocked_stages = [1]  # Stage 1 is open by default; Stage 2+ locked
        self.stage_scores = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        self.organizer_url = organizer_url
        self.load()

    def is_registered(self):
        return bool(self.name.strip() and self.class_name.strip())

    def register(self, name, class_name):
        self.name = name.strip()
        self.class_name = class_name.strip()
        self.save()
        self.sync_score()

    def is_stage_unlocked(self, stage_num):
        # Check local unlocked list first
        if stage_num in self.unlocked_stages:
            return True
            
        # If connected to an active organizer server, check remote unlocked list
        if self.organizer_url:
            try:
                req = urllib.request.Request(f"{self.organizer_url.rstrip('/')}/api/status", headers={"User-Agent": "GitClient/1.0"})
                with urllib.request.urlopen(req, timeout=1.5) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    unlocked = data.get("unlocked", [1])
                    if stage_num in unlocked:
                        if stage_num not in self.unlocked_stages:
                            self.unlocked_stages.append(stage_num)
                            self.save()
                        return True
            except Exception:
                pass
                
        return False

    def unlock_stage(self, stage_num, password=None):
        """Unlock a stage via organizer password or remote authorization."""
        if stage_num in self.unlocked_stages:
            return True, "Stage already unlocked."
            
        expected = STAGE_PASSWORDS.get(stage_num)
        if password and expected and (password.strip().upper() == expected.upper() or password.strip().upper() == expected.replace("26", "").upper()):
            self.unlocked_stages.append(stage_num)
            self.save()
            return True, f"Stage {stage_num} ({STAGE_NAMES.get(stage_num)}) unlocked successfully!"
            
        return False, "Invalid unlock passcode. Please wait for the workshop organizer to reveal it on screen."

    def add_points(self, stage_num, points):
        """Add points to total and stage, and sync to leaderboard."""
        self.score += points
        st_key = str(stage_num)
        self.stage_scores[st_key] = self.stage_scores.get(st_key, 0) + points
        self.save()
        self.sync_score()
        return self.score

    def save(self):
        data = {
            "name": self.name,
            "class_name": self.class_name,
            "score": self.score,
            "unlocked_stages": self.unlocked_stages,
            "stage_scores": self.stage_scores,
            "organizer_url": self.organizer_url,
            "last_updated": time.time()
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.name = data.get("name", self.name)
                    self.class_name = data.get("class_name", self.class_name)
                    self.score = data.get("score", self.score)
                    self.unlocked_stages = data.get("unlocked_stages", [1])
                    self.stage_scores = data.get("stage_scores", self.stage_scores)
                    self.organizer_url = data.get("organizer_url", self.organizer_url)
            except Exception:
                pass

    def sync_score(self):
        """Update local leaderboard and optionally push to organizer server."""
        if not self.is_registered():
            return
            
        # Update local leaderboard.json
        update_local_leaderboard(self.name, self.class_name, self.score, self.stage_scores)
        
        # If organizer URL set, push over LAN
        if self.organizer_url:
            try:
                payload = json.dumps({
                    "name": self.name,
                    "class_name": self.class_name,
                    "score": self.score,
                    "stage_scores": self.stage_scores
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.organizer_url.rstrip('/')}/api/score",
                    data=payload,
                    headers={"Content-Type": "application/json", "User-Agent": "GitClient/1.0"}
                )
                urllib.request.urlopen(req, timeout=1.5)
            except Exception:
                pass


def get_leaderboard(limit=15):
    """Retrieve top participants sorted by score descending."""
    entries = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []
            
    # Sort by score desc, then time asc
    entries.sort(key=lambda x: (-x.get("score", 0), x.get("timestamp", 0)))
    return entries[:limit]


def update_local_leaderboard(name, class_name, score, stage_scores=None):
    """Update or append player record in shared local leaderboard file."""
    entries = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []

    # Find existing player by name & class
    found = False
    for entry in entries:
        if entry.get("name", "").strip().lower() == name.strip().lower() and \
           entry.get("class_name", "").strip().lower() == class_name.strip().lower():
            # Update score if higher or changed
            entry["score"] = max(entry.get("score", 0), score)
            entry["stage_scores"] = stage_scores or entry.get("stage_scores", {})
            entry["timestamp"] = time.time()
            found = True
            break

    if not found:
        entries.append({
            "name": name.strip(),
            "class_name": class_name.strip(),
            "score": score,
            "stage_scores": stage_scores or {},
            "timestamp": time.time()
        })

    entries.sort(key=lambda x: (-x.get("score", 0), x.get("timestamp", 0)))

    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except Exception:
        pass
