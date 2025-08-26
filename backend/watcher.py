import os
import json
from parse import parse_log_lines 
import logging
from dotenv import load_dotenv

load_dotenv()
level_name = os.getenv("LOGGING_LEVEL", "INFO").upper()
level = getattr(logging, level_name, logging.INFO) 

logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s")


LOG_PATH = "/hostlog/auth.log"      
if not LOG_PATH:
    raise ValueError("SSH_LOG environment variable not set")  

ROTATED_PATH = "/hostlog/auth.log.1"
if not ROTATED_PATH:    
    raise ValueError("SSH_LOG_ROLL environment variable not set")   
STATE_FILE = "/state/state.json"                                             


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
        logging.error(f"Error reading log: {e}")
        return [], offset

def run_watcher():
    logging.info("Starting sshame watcher...")
    state = load_state()

    while True:
        current_inode = get_inode(LOG_PATH)

        # Fall 1: Gleiches Logfile → lese ab letzter Position
        if state["inode"] == current_inode:
            lines, new_offset = read_new_lines(LOG_PATH, state["offset"])
            parse_log_lines(lines)
            state["offset"] = new_offset

        # Fall 2: Log wurde rotiert → lese log.1 vollständig + log neu ab 0
        else:
            logging.info("Log rotation detected – scanning auth.log.1")
            old_lines, _ = read_new_lines(ROTATED_PATH, 0)
            parse_log_lines(old_lines)
            new_lines, new_offset = read_new_lines(LOG_PATH, 0)
            parse_log_lines(new_lines)
            state["inode"] = current_inode
            state["offset"] = new_offset

        save_state(state)

if __name__ == "__main__":
    run_watcher()
