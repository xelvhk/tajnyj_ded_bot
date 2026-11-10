"""Persistent state for a single Secret Santa event."""
import secrets
from datetime import datetime, timezone
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'santas.db'


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def start_record():
    with connect() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, user_id INTEGER UNIQUE, username TEXT,
            santa_for INTEGER, gift TEXT)''')


def register(user_id, name):
    with connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute('SELECT 1 FROM users WHERE user_id=?', (user_id,)).fetchone():
            return 'existing'
        if conn.execute('SELECT 1 FROM users WHERE santa_for IS NOT NULL').fetchone():
            return 'closed'
        conn.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, name))
        return 'registered'


def save_gift(user_id, gift):
    with connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute('SELECT 1 FROM users WHERE santa_for IS NOT NULL').fetchone():
            return False
        return conn.execute('UPDATE users SET gift=? WHERE user_id=?', (gift, user_id)).rowcount > 0


def status():
    with connect() as conn:
        return conn.execute('SELECT COUNT(*), COUNT(gift), COUNT(santa_for) FROM users').fetchone()


def assignment(user_id):
    with connect() as conn:
        return conn.execute('''SELECT u.gift, r.username, r.gift FROM users u
            LEFT JOIN users r ON r.user_id = u.santa_for WHERE u.user_id=?''', (user_id,)).fetchone()


def draw():
    with connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        if conn.execute('SELECT 1 FROM users WHERE santa_for IS NOT NULL').fetchone():
            return []
        ids = [row[0] for row in conn.execute('SELECT user_id FROM users WHERE gift IS NOT NULL')]
        if len(ids) < 2:
            return []
        secrets.SystemRandom().shuffle(ids)
        conn.executemany('UPDATE users SET santa_for=? WHERE user_id=?',
                         [(ids[(i + 1) % len(ids)], user_id) for i, user_id in enumerate(ids)])
        return ids


def assigned_ids():
    with connect() as conn:
        return [row[0] for row in conn.execute('SELECT user_id FROM users WHERE santa_for IS NOT NULL')]


def new_game():
    """Archive the current event database and clear it for a new event."""
    with connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        if not count:
            return None
        archive = DB_PATH.parent / 'archive'
        archive.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup_path = archive / f'santas-{stamp}.db'
        try:
            # The source transaction is committed before SQLite's backup API runs.
            conn.commit()
            with sqlite3.connect(backup_path) as backup:
                conn.backup(backup)
            conn.execute('BEGIN IMMEDIATE')
            conn.execute('DELETE FROM users')
        except Exception:
            backup_path.unlink(missing_ok=True)
            raise
        return backup_path


def roster():
    with connect() as conn:
        return conn.execute('SELECT username, gift IS NOT NULL FROM users ORDER BY username, user_id').fetchall()
