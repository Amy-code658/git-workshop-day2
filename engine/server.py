"""
server.py - Central Workshop Hub Server & REST API for FOSS MEC Git Workshop.
Handles live participant registration, real-time leaderboard syncing,
organizer remote stage unlock broadcast, and randomized question distribution.
Zero external dependencies (pure Python standard library).
"""

import os
import sys
import json
import random
import socket
import threading
import time
import http.server
import socketserver
import urllib.parse
from engine.state import (
    PlayerState, get_leaderboard, STAGE_PASSWORDS,
    format_seconds, get_first_finishers, get_workshop_status,
    set_workshop_status, update_local_leaderboard, check_and_award_first_finisher,
    get_lan_ip
)
from engine.quest import GitQuestValidator, generate_verification_token

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")
CONTENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")

def load_json_file(filename):
    path = os.path.join(CONTENT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

class WorkshopHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, format, *args):
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Workshop Status (Auto-polled by all student laptops every 2s)
        if path == "/api/status":
            st = get_workshop_status()
            self.send_json({
                "unlocked": st.get("unlocked", [1]),
                "current_stage": st.get("current_stage", 1),
                "first_finishers": get_first_finishers(),
                "workshop": "FOSS MEC Git Workshop"
            })
            return

        # 2. Live Leaderboard (Auto-polled by all student laptops every 2s)
        elif path == "/api/leaderboard":
            raw_entries = get_leaderboard(limit=50)
            entries = []
            for e in raw_entries:
                item = dict(e)
                item["formatted_time"] = format_seconds(e.get("total_time", 0.0))
                entries.append(item)
            self.send_json(entries)
            return

        # 3. Randomized Final Showdown Questions (Each participant gets 10 random questions from 35-pool)
        elif path == "/api/showdown/questions":
            bank = load_json_file("questions_bank.json")
            count = int(query.get("count", [10])[0])
            count = max(5, min(count, len(bank)))
            selected = random.sample(bank, count)
            self.send_json(selected)
            return

        # 4. Randomized Detective Cases (Each participant gets 6 random cases from 12-pool)
        elif path == "/api/detective/cases":
            cases = load_json_file("detective_cases.json")
            count = int(query.get("count", [6])[0])
            count = max(3, min(count, len(cases)))
            selected = random.sample(cases, count)
            self.send_json(selected)
            return

        # 5. Randomized Bingo Items (Random 9 for unique card + full pool for caller)
        elif path == "/api/bingo/items":
            items = load_json_file("bingo_data.json")
            self.send_json(items)
            return

        # 6. Static files
        if path == "/" or not path:
            self.path = "/index.html"
            
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(post_data.decode("utf-8"))
        except Exception:
            body = {}

        # 1. Player Registration
        if path == "/api/register":
            name = body.get("name", "").strip()
            class_name = body.get("class_name", "").strip()
            score = int(body.get("score", 0))
            total_time = float(body.get("total_time", 0.0))
            
            if name and class_name:
                update_local_leaderboard(name, class_name, score, total_time)
                
            self.send_json({
                "success": True,
                "name": name,
                "class_name": class_name,
                "score": score,
                "total_time": total_time,
                "formatted_time": format_seconds(total_time)
            })
            return

        # 2. Score & Time Update (Live Leaderboard Sync)
        elif path == "/api/score":
            name = body.get("name", "").strip()
            class_name = body.get("class_name", "").strip()
            stage_num = int(body.get("stage", 1))
            points = int(body.get("points", 0))
            time_taken = float(body.get("time_taken", 0.0))
            is_completion = bool(body.get("is_completion", False))

            bonus_pts = 0
            is_first = False
            if is_completion and name:
                is_first, bonus_pts = check_and_award_first_finisher(stage_num, name)

            total_added = points + bonus_pts

            # Update in shared leaderboard
            entries = get_leaderboard(limit=100)
            player_record = None
            for e in entries:
                if e.get("name", "").strip().lower() == name.lower() and \
                   e.get("class_name", "").strip().lower() == class_name.lower():
                    player_record = e
                    break

            new_score = total_added
            new_total_time = time_taken
            stage_scores = {}
            stage_times = {}

            if player_record:
                stage_scores = player_record.get("stage_scores", {})
                stage_times = player_record.get("stage_times", {})
                st_k = str(stage_num)
                stage_scores[st_k] = stage_scores.get(st_k, 0) + total_added
                if time_taken > 0:
                    stage_times[st_k] = round(stage_times.get(st_k, 0.0) + time_taken, 1)

                new_score = player_record.get("score", 0) + total_added
                new_total_time = round(sum(stage_times.values()), 1)
            else:
                st_k = str(stage_num)
                stage_scores[st_k] = total_added
                if time_taken > 0:
                    stage_times[st_k] = time_taken

            if name and class_name:
                update_local_leaderboard(
                    name, class_name, new_score, new_total_time, stage_scores, stage_times
                )

            self.send_json({
                "success": True,
                "score": new_score,
                "total_time": new_total_time,
                "formatted_time": format_seconds(new_total_time),
                "is_first": is_first,
                "bonus_pts": bonus_pts
            })
            return

        # 3. Stage Unlock (Triggered by Organizer or Student Passcode)
        elif path == "/api/unlock":
            stage_num = int(body.get("stage", 2))
            pwd = body.get("password", "").strip()
            
            expected = STAGE_PASSWORDS.get(stage_num)
            st = get_workshop_status()
            unlocked = st.get("unlocked", [1])

            if stage_num in unlocked:
                self.send_json({"success": True, "message": "Stage already unlocked.", "unlocked": unlocked})
                return

            if pwd and expected and (pwd.upper() == expected.upper() or pwd.upper() == expected.replace("26", "").upper()):
                unlocked.append(stage_num)
                set_workshop_status(unlocked, current_stage=stage_num)
                self.send_json({
                    "success": True,
                    "message": f"Stage {stage_num} unlocked successfully!",
                    "unlocked": unlocked
                })
                return

            self.send_json({
                "success": False,
                "message": "Invalid unlock passcode. Wait for the workshop organizer to reveal it on screen.",
                "unlocked": unlocked
            })
            return

        # 4. Organizer Stage Control API (Direct master toggle)
        elif path == "/api/organizer/toggle-stage":
            stage_num = int(body.get("stage", 2))
            action = body.get("action", "unlock")
            
            st = get_workshop_status()
            unlocked = st.get("unlocked", [1])
            
            if action == "unlock":
                if stage_num not in unlocked:
                    unlocked.append(stage_num)
            elif action == "lock":
                if stage_num in unlocked and stage_num != 1:
                    unlocked.remove(stage_num)

            set_workshop_status(unlocked, current_stage=stage_num)
            self.send_json({"success": True, "unlocked": unlocked})
            return

        # 5. Git Quest Evaluation
        elif path == "/api/quest/verify":
            repo_path = body.get("repo_path", "").strip() or os.getcwd()
            name = body.get("name", "Student")
            time_taken = float(body.get("time_taken", 0.0))
            
            validator = GitQuestValidator(repo_path=os.path.abspath(os.path.expanduser(repo_path)), student_name=name)
            task_flags = validator.evaluate()
            token = generate_verification_token(name, validator.total_score, task_flags)
            
            self.send_json({
                "success": True,
                "total_score": validator.total_score,
                "token": token,
                "results": validator.results
            })
            return

        self.send_response(404)
        self.end_headers()


def start_udp_beacon(port=5000):
    """Broadcast UDP beacon every 2 seconds so students on Wi-Fi auto-discover the hub."""
    def beacon_loop():
        lan_ip = get_lan_ip()
        msg = json.dumps({"workshop": "foss-mec", "ip": lan_ip, "port": port}).encode("utf-8")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            try:
                sock.sendto(msg, ("255.255.255.255", 5005))
            except Exception:
                pass
            time.sleep(2)

    t = threading.Thread(target=beacon_loop, daemon=True)
    t.start()


def discover_hub_ip(timeout=1.0):
    """Listen for organizer UDP beacon on LAN. Returns URL string or None."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    try:
        sock.bind(("", 5005))
        data, _ = sock.recvfrom(1024)
        info = json.loads(data.decode("utf-8"))
        if info.get("workshop") == "foss-mec" and info.get("ip"):
            return f"http://{info['ip']}:{info.get('port', 5000)}"
    except Exception:
        pass
    finally:
        sock.close()
    return None


def start_hub_server(port=5000, start_beacon=True):
    """Start central workshop hub server."""
    server = None
    actual_port = port
    for p in range(port, port + 20):
        try:
            # Bind to 0.0.0.0 so whole Wi-Fi network can connect!
            server = socketserver.TCPServer(("0.0.0.0", p), WorkshopHTTPHandler)
            actual_port = p
            break
        except OSError:
            continue
            
    if not server:
        raise RuntimeError("Could not find an available port to launch hub server.")
        
    if start_beacon:
        start_udp_beacon(actual_port)
        
    return server, actual_port
