"""
server.py - Zero-dependency Python HTTP Server & REST API for the Game Interface.
Serves web game client on localhost and handles participant registration,
real-time score & timer reporting, and live Git repository grading via standard library.
"""

import os
import sys
import json
import http.server
import socketserver
import urllib.parse
from engine.state import (
    PlayerState, get_leaderboard, STAGE_PASSWORDS,
    format_seconds, get_first_finishers
)
from engine.bingo import load_bingo_items
from engine.detective import load_detective_cases
from engine.showdown import load_showdown_questions
from engine.quest import GitQuestValidator, generate_verification_token

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")

class WorkshopHTTPHandler(http.server.SimpleHTTPRequestHandler):
    player_state = None

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

        if path == "/api/profile":
            st = self.player_state or PlayerState()
            self.send_json({
                "name": st.name,
                "class_name": st.class_name,
                "score": st.score,
                "total_time": st.total_time,
                "formatted_time": format_seconds(st.total_time),
                "stage_scores": st.stage_scores,
                "stage_times": st.stage_times,
                "unlocked_stages": st.unlocked_stages
            })
            return
            
        elif path == "/api/status":
            st = self.player_state or PlayerState()
            self.send_json({
                "unlocked": st.unlocked_stages,
                "score": st.score,
                "total_time": st.total_time,
                "formatted_time": format_seconds(st.total_time),
                "first_finishers": get_first_finishers()
            })
            return

        elif path == "/api/leaderboard":
            raw_entries = get_leaderboard(limit=25)
            # Add formatted_time to each entry
            entries = []
            for e in raw_entries:
                item = dict(e)
                item["formatted_time"] = format_seconds(e.get("total_time", 0.0))
                entries.append(item)
            self.send_json(entries)
            return

        elif path == "/api/bingo/items":
            self.send_json(load_bingo_items())
            return

        elif path == "/api/detective/cases":
            self.send_json(load_detective_cases())
            return

        elif path == "/api/showdown/questions":
            self.send_json(load_showdown_questions())
            return

        # Default static file routing
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

        st = self.player_state or PlayerState()

        if path == "/api/register":
            name = body.get("name", "")
            class_name = body.get("class_name", "")
            st.register(name, class_name)
            self.send_json({
                "success": True,
                "name": st.name,
                "class_name": st.class_name,
                "score": st.score,
                "total_time": st.total_time,
                "formatted_time": format_seconds(st.total_time),
                "unlocked_stages": st.unlocked_stages
            })
            return

        elif path == "/api/score":
            stage_num = int(body.get("stage", 1))
            points = int(body.get("points", 0))
            time_taken = float(body.get("time_taken", 0.0))
            is_completion = bool(body.get("is_completion", False))
            
            new_score, is_first, bonus_pts = st.add_game_result(
                stage_num, points, time_taken, is_completion
            )
            self.send_json({
                "success": True,
                "score": new_score,
                "total_time": st.total_time,
                "formatted_time": format_seconds(st.total_time),
                "is_first": is_first,
                "bonus_pts": bonus_pts
            })
            return

        elif path == "/api/unlock":
            stage_num = int(body.get("stage", 2))
            pwd = body.get("password", "")
            success, msg = st.unlock_stage(stage_num, pwd)
            self.send_json({"success": success, "message": msg, "unlocked": st.unlocked_stages})
            return

        elif path == "/api/quest/verify":
            repo_path = body.get("repo_path", "").strip() or os.getcwd()
            time_taken = float(body.get("time_taken", 0.0))
            validator = GitQuestValidator(repo_path=os.path.abspath(os.path.expanduser(repo_path)), student_name=st.name)
            task_flags = validator.evaluate()
            token = generate_verification_token(st.name, validator.total_score, task_flags)
            
            # If 100 points, mark completion
            is_complete = (validator.total_score == 100)
            new_score, is_first, bonus_pts = st.add_game_result(
                4, validator.total_score, time_taken, is_complete
            )
            
            self.send_json({
                "success": True,
                "total_score": validator.total_score,
                "score": new_score,
                "token": token,
                "results": validator.results,
                "total_time": st.total_time,
                "formatted_time": format_seconds(st.total_time),
                "is_first": is_first,
                "bonus_pts": bonus_pts
            })
            return

        self.send_response(404)
        self.end_headers()


def start_game_server(player_state, port=5000):
    WorkshopHTTPHandler.player_state = player_state
    server = None
    actual_port = port
    for p in range(port, port + 20):
        try:
            server = socketserver.TCPServer(("0.0.0.0", p), WorkshopHTTPHandler)
            actual_port = p
            break
        except OSError:
            continue
            
    if not server:
        raise RuntimeError("Could not find an available port to launch game server.")
        
    return server, actual_port
