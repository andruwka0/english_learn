"""SQLite persistence helpers for recording adaptive test sessions."""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "adaptive_test.db"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tests (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                start_level TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                current_part TEXT,
                paused INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                domain TEXT NOT NULL,
                score REAL NOT NULL,
                answered_at TEXT NOT NULL,
                FOREIGN KEY(test_id) REFERENCES tests(id)
            )
            """
        )
        connection.commit()


def reset_db() -> None:
    with _connect() as connection:
        connection.execute("DELETE FROM responses")
        connection.execute("DELETE FROM tests")
        connection.commit()


def record_test_start(
    test_id: str,
    first_name: str,
    last_name: str,
    start_level: str,
    started_at: datetime,
    upcoming_part: Optional[str],
) -> None:
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO tests (id, first_name, last_name, start_level, started_at, current_part, paused)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(id) DO UPDATE SET
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                start_level=excluded.start_level,
                started_at=excluded.started_at,
                current_part=excluded.current_part,
                paused=1,
                finished_at=NULL
            """,
            (
                test_id,
                first_name,
                last_name,
                start_level,
                started_at.isoformat(),
                upcoming_part,
            ),
        )
        connection.commit()


def update_test_state(test_id: str, current_part: Optional[str], paused: bool) -> None:
    with _connect() as connection:
        connection.execute(
            """
            UPDATE tests
               SET current_part = ?,
                   paused = ?
             WHERE id = ?
            """,
            (current_part, int(paused), test_id),
        )
        connection.commit()


def record_response(test_id: str, item_id: str, domain: str, score: float, answered_at: datetime) -> None:
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO responses (test_id, item_id, domain, score, answered_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (test_id, item_id, domain, score, answered_at.isoformat()),
        )
        connection.commit()


def record_test_finish(test_id: str, finished_at: datetime) -> None:
    with _connect() as connection:
        connection.execute(
            """
            UPDATE tests
               SET finished_at = ?,
                   paused = 0,
                   current_part = NULL
             WHERE id = ?
            """,
            (finished_at.isoformat(), test_id),
        )
        connection.commit()


__all__ = [
    "DB_PATH",
    "init_db",
    "record_response",
    "record_test_finish",
    "record_test_start",
    "reset_db",
    "update_test_state",
]
