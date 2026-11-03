"""
state.py - Profile, Live Leaderboard, Stage Lock, and Time-Tracking Management.
FOSS MEC Git Workshop Day 2.
Zero external dependencies (pure Python standard library).
"""

import os
import json
import time
import socket
import urllib.request
import urllib.error

SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".player_save.json")
LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "leaderboard.json")
FIRST_FINISHERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".first_finishers.json")
STATUS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workshop_status.json")

# Stage Unlock Keys
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

def get_lan_ip():
    """Detect the local LAN/Wi-Fi IP of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def format_seconds(seconds):
    """Format seconds into MM:SS string."""
    try:
        s = int(round(float(seconds)))
        mins = s // 60
        secs = s % 60
        return f"{mins:02d}:{secs:02d}"
    except (ValueError, TypeError):
        return "00:00"

def get_workshop_status():
    """Read central workshop status (unlocked stages, current active stage)."""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"unlocked": [1], "current_stage": 1, "last_updated": time.time()}

def set_workshop_status(unlocked_stages, current_stage=None):
    """Save central workshop status."""
    data = {
        "unlocked": sorted(list(set(unlocked_stages))),
        "current_stage": current_stage or (max(unlocked_stages) if unlocked_stages else 1),
        "last_updated": time.time()
    }
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
    return data

def get_first_finishers():
    """Retrieve mapping of stage -> first finisher name."""
    if os.path.exists(FIRST_FINISHERS_FILE):
        try:
            with open(FIRST_FINISHERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def check_and_award_first_finisher(stage_num, player_name):
    """Check if player is the first person to finish this stage; awards 100 bonus pts."""
    st_key = str(stage_num)
    finishers = get_first_finishers()
    
    if st_key not in finishers or not finishers[st_key]:
        finishers[st_key] = player_name.strip()
        try:
            with open(FIRST_FINISHERS_FILE, "w", encoding="utf-8") as f:
                json.dump(finishers, f, indent=2)
        except Exception:
            pass
        return True, 100  # First finisher! +100 bonus points
        
    return False, 0


class PlayerState:
    def __init__(self, name="", class_name="", hub_url=None):
        self.name = name
        self.class_name = class_name
        self.score = 0
        self.unlocked_stages = [1]
        self.stage_scores = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        self.stage_times = {"1": 0.0, "2": 0.0, "3": 0.0, "4": 0.0, "5": 0.0}
        self.total_time = 0.0
        self.hub_url = hub_url
        self.load()

    def is_registered(self):
        return bool(self.name.strip() and self.class_name.strip())

    def register(self, name, class_name):
        self.name = name.strip()
        self.class_name = class_name.strip()
        self.save()
        self.sync_score()

    def is_stage_unlocked(self, stage_num):
        # 1. If connected to an active central organizer hub, fetch status
        if self.hub_url:
            try:
                req = urllib.request.Request(f"{self.hub_url.rstrip('/')}/api/status", headers={"User-Agent": "GitClient/1.0"})
                with urllib.request.urlopen(req, timeout=1.5) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    unlocked = data.get("unlocked", [1])
                    self.unlocked_stages = unlocked
                    return stage_num in unlocked
            except Exception:
                pass

        # 2. Check local file status
        status = get_workshop_status()
        unlocked = status.get("unlocked", [1])
        if stage_num in unlocked:
            return True

        return stage_num in self.unlocked_stages

    def unlock_stage(self, stage_num, password=None):
        if stage_num in self.unlocked_stages:
            return True, "Stage already unlocked."
            
        expected = STAGE_PASSWORDS.get(stage_num)
        if password and expected and (password.strip().upper() == expected.upper() or password.strip().upper() == expected.replace("26", "").upper()):
            if stage_num not in self.unlocked_stages:
                self.unlocked_stages.append(stage_num)
            self.save()
            
            # If hub url present, notify hub
            if self.hub_url:
                try:
                    payload = json.dumps({"stage": stage_num, "password": password}).encode("utf-8")
                    req = urllib.request.Request(
                        f"{self.hub_url.rstrip('/')}/api/unlock",
                        data=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    urllib.request.urlopen(req, timeout=1.5)
                except Exception:
                    pass
            else:
                # Update local workshop status
                st = get_workshop_status()
                unl = st.get("unlocked", [1])
                if stage_num not in unl:
                    unl.append(stage_num)
                    set_workshop_status(unl)
                    
            return True, f"Stage {stage_num} ({STAGE_NAMES.get(stage_num)}) unlocked successfully!"
            
        return False, "Invalid unlock passcode. Please wait for the workshop organizer to reveal it on screen."

    def add_game_result(self, stage_num, points, time_taken=0.0, is_completion=False):
        """Add points and time taken for a game. Syncs to central hub."""
        st_key = str(stage_num)
        
        # If hub url configured, sync with hub
        if self.hub_url:
            try:
                payload = json.dumps({
                    "name": self.name,
                    "class_name": self.class_name,
                    "stage": stage_num,
                    "points": points,
                    "time_taken": time_taken,
                    "is_completion": is_completion
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.hub_url.rstrip('/')}/api/score",
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=2.0) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    self.score = data.get("score", self.score)
                    self.total_time = data.get("total_time", self.total_time)
                    return self.score, data.get("is_first", False), data.get("bonus_pts", 0)
            except Exception:
                pass

        # Local fallback
        bonus_pts = 0
        is_first = False
        if is_completion and self.is_registered():
            is_first, bonus_pts = check_and_award_first_finisher(stage_num, self.name)
            
        total_pts = points + bonus_pts
        self.score += total_pts
        self.stage_scores[st_key] = self.stage_scores.get(st_key, 0) + total_pts
        
        if time_taken > 0:
            self.stage_times[st_key] = round(self.stage_times.get(st_key, 0.0) + float(time_taken), 1)
            self.total_time = round(sum(self.stage_times.values()), 1)
            
        self.save()
        self.sync_score()
        return self.score, is_first, bonus_pts

    def save(self):
        data = {
            "name": self.name,
            "class_name": self.class_name,
            "score": self.score,
            "unlocked_stages": self.unlocked_stages,
            "stage_scores": self.stage_scores,
            "stage_times": self.stage_times,
            "total_time": self.total_time,
            "hub_url": self.hub_url,
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
                    self.stage_times = data.get("stage_times", self.stage_times)
                    self.total_time = data.get("total_time", self.total_time)
                    self.hub_url = data.get("hub_url", self.hub_url)
            except Exception:
                pass

    def sync_score(self):
        if not self.is_registered():
            return
            
        # Update local file
        update_local_leaderboard(
            self.name, self.class_name, self.score,
            self.total_time, self.stage_scores, self.stage_times
        )

        # If hub url, register on hub
        if self.hub_url:
            try:
                payload = json.dumps({
                    "name": self.name,
                    "class_name": self.class_name,
                    "score": self.score,
                    "total_time": self.total_time
                }).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.hub_url.rstrip('/')}/api/register",
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )
                urllib.request.urlopen(req, timeout=1.5)
            except Exception:
                pass


def get_leaderboard(limit=50):
    """Retrieve all participants sorted by score descending, then total time ascending (tie-breaker!)."""
    entries = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []
            
    # Sort: Higher score first (-score), then least total time (+total_time)
    entries.sort(key=lambda x: (-x.get("score", 0), x.get("total_time", 999999), x.get("timestamp", 0)))
    return entries[:limit]


def update_local_leaderboard(name, class_name, score, total_time=0.0, stage_scores=None, stage_times=None):
    """Update or append player record in shared local leaderboard file."""
    if not name or not class_name:
        return
        
    entries = []
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception:
            entries = []

    found = False
    for entry in entries:
        if entry.get("name", "").strip().lower() == name.strip().lower() and \
           entry.get("class_name", "").strip().lower() == class_name.strip().lower():
            entry["score"] = max(entry.get("score", 0), score)
            entry["total_time"] = round(total_time, 1) if total_time > 0 else entry.get("total_time", 0.0)
            if stage_scores:
                entry["stage_scores"] = stage_scores
            if stage_times:
                entry["stage_times"] = stage_times
            entry["timestamp"] = time.time()
            found = True
            break

    if not found:
        entries.append({
            "name": name.strip(),
            "class_name": class_name.strip(),
            "score": score,
            "total_time": round(total_time, 1),
            "stage_scores": stage_scores or {},
            "stage_times": stage_times or {},
            "timestamp": time.time()
        })

    entries.sort(key=lambda x: (-x.get("score", 0), x.get("total_time", 999999), x.get("timestamp", 0)))

    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except Exception:
        pass
