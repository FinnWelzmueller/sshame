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
        return {"inode": None, "offset": 0}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: str):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def get_inode(path: str):
    try:
        return os.stat(path).st_ino
    except FileNotFoundError:
        return None


def get_size(path: str):
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return 0


def read_new_lines(log_path: str, offset: int):
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

    # Initialization
    if state["inode"] is None:
        state["inode"] = get_inode(LOG_PATH)
        state["offset"] = 0
        save_state(state)

    while True:
        current_inode = get_inode(LOG_PATH)

        # No rotation detected -> business as usual
        if current_inode == state["inode"]:
            # copy/truncate -> scall whole file
            current_size = get_size(LOG_PATH)
            if state["offset"] > current_size:
                logging.info("Detected copytruncate/truncation – resetting offset to 0")
                state["offset"] = 0

            lines, new_offset = read_new_lines(LOG_PATH, state["offset"])
            if lines:
                parse_log_lines(lines)
                state["offset"] = new_offset
                save_state(state)

        # rotation detected -> scan old file from last offset and new file from 0
        else:
            logging.info("Log rotation detected")

            # scan old file
            rotated_inode = get_inode(ROTATED_PATH)
            if rotated_inode == state["inode"]:
                logging.info("Reading rest of old file")
                old_lines, _ = read_new_lines(ROTATED_PATH, state["offset"])
                if old_lines:
                    parse_log_lines(old_lines)
            else:
                logging.info("Previous file not found as auth.log.1 (skipping)")

            # scan new file
            new_lines, new_offset = read_new_lines(LOG_PATH, 0)
            if new_lines:
                parse_log_lines(new_lines)

            # set state
            state["inode"] = current_inode
            state["offset"] = new_offset if new_lines else 0
            save_state(state)


if __name__ == "__main__":
    run_watcher()
