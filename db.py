import sqlite3
from contextlib import contextmanager

DB = "polls.db"


def conn():
    return sqlite3.connect(DB)


@contextmanager
def get_db():
    c = conn()
    try:
        yield c
    finally:
        c.close()


def init():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS polls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            created_by TEXT NOT NULL,
            closed INTEGER NOT NULL DEFAULT 0
        )
        """)
        try:
            db.execute("ALTER TABLE polls ADD COLUMN closed INTEGER NOT NULL DEFAULT 0")
        except Exception:
            pass
        db.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            poll_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            option_index INTEGER NOT NULL,
            PRIMARY KEY (poll_id, user_id),
            FOREIGN KEY (poll_id) REFERENCES polls(id)
        )
        """)
        db.commit()
