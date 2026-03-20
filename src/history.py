"""
history.py
Persist and retrieve query history as a local JSON file.
"""

import json
from pathlib import Path
from datetime import datetime

import tempfile
HISTORY_FILE = Path(tempfile.gettempdir()) / "query_history.json"
MAX_HISTORY = 50


def load_history() -> list[dict]:
    """Return list of history entries (newest last)."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_to_history(question: str, sql: str) -> None:
    """Append a new entry, avoiding exact duplicates."""
    question = question.strip()
    sql = sql.strip()
    history = load_history()

    # Deduplicate by question text
    if any(h["question"] == question for h in history):
        return

    history.append({
        "question":  question,
        "sql":       sql,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })

    # Rolling window
    history = history[-MAX_HISTORY:]

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def clear_history() -> None:
    """Wipe all stored history."""
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()