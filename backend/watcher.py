import os
import time
import json
from datetime import datetime
from parse import parse_log_lines  # ← deine Parserfunktion für Zeilen
from influx import write_ssh_event  # ← deine Influx-Funktion

LOG_PATH = "./auth.log"            
ROTATED_PATH = "./auth.log.1"      
STATE_FILE = "state.json"                 
INTERVAL = 30                             

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"inode": None, "offset": 0}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_inode(path):
    try:
        return os.stat(path).st_ino
    except FileNotFoundError:
        return None

def read_new_lines(log_path, offset):
    try:
        with open(log_path, "r") as f:
            f.seek(offset)
            lines = f.readlines()
            new_offset = f.tell()
        return lines, new_offset
    except Exception as e:
        print(f"Error reading log: {e}")
        return [], offset

def process_lines(lines):
    events = parse_log_lines(lines)
    for event in events:
        # event = (ip, user, timestamp_str, port)
        write_ssh_event(*event)

def run_watcher():
    print("Starting sshame watcher...")
    state = load_state()

    while True:
        current_inode = get_inode(LOG_PATH)

        # Fall 1: Gleiches Logfile → lese ab letzter Position
        if state["inode"] == current_inode:
            lines, new_offset = read_new_lines(LOG_PATH, state["offset"])
            process_lines(lines)
            state["offset"] = new_offset

        # Fall 2: Log wurde rotiert → lese log.1 vollständig + log neu ab 0
        else:
            print("Log rotation detected – scanning auth.log.1")
            old_lines, _ = read_new_lines(ROTATED_PATH, 0)
            process_lines(old_lines)
            new_lines, new_offset = read_new_lines(LOG_PATH, 0)
            process_lines(new_lines)
            state["inode"] = current_inode
            state["offset"] = new_offset

        save_state(state)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    run_watcher()
