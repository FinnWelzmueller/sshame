import os
import json
from parse import parse_log_lines
import logging
from dotenv import load_dotenv
import time

load_dotenv()
level_name = os.getenv("LOGGING_LEVEL", "INFO").upper()
level = getattr(logging, level_name, logging.INFO)

logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)

LOG_PATH = "/hostlog/auth.log"
if not LOG_PATH:
    raise ValueError("SSH_LOG environment variable not set")

ROTATED_PATH = "/hostlog/auth.log.1"
if not ROTATED_PATH:
    raise ValueError("SSH_LOG_ROLL environment variable not set")

STATE_FILE = "/state/state.json"



def load_state():
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE, "r") as f:
        return json.load(f)["last_row"]
    

def save_state(last_row: int):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"last_row": last_row}, f)

def read_lines(path:str) -> list[str]:
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        return lines
    except Exception as e:
        logging.error(f"Error reading log: {e}")
        return []

def read_new_lines() -> list[str]:
    last_row = load_state()
    lines = read_lines(LOG_PATH)
    out = lines[last_row:]
    if len(lines) < last_row:   # Check for log rotation
        logging.info("Log file rotation detected. Reading old file first.")
        old_lines = read_lines(ROTATED_PATH)
        out = old_lines[last_row:] + lines
    save_state(len(lines))
    return out




def run_watcher():
    logging.info("Starting sshame watcher...")

    while True:
        new_lines = read_new_lines()
        logging.info(f"Found {len(new_lines)} new lines.")
        parse_log_lines(new_lines)
        time.sleep(10)


if __name__ == "__main__":
    run_watcher()
