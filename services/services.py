"""Persistent state for a single Secret Santa event."""
import secrets
import hashlib
import time
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
        columns = {row[1] for row in conn.execute('PRAGMA table_info(users)')}
        if 'notification_pending' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN notification_pending INTEGER NOT NULL DEFAULT 0')
        conn.execute('''CREATE TABLE IF NOT EXISTS confirmations (
            admin_id INTEGER, action TEXT, token TEXT, snapshot TEXT,
            expires_at INTEGER, PRIMARY KEY (admin_id, action))''')


def snapshot(conn):
    rows = conn.execute('SELECT user_id, username, gift, santa_for FROM users ORDER BY user_id').fetchall()
    return hashlib.sha256(repr(rows).encode()).hexdigest()


def preview(admin_id, action):
    with connect() as conn:
        token = secrets.token_urlsafe(8)
        conn.execute('''INSERT OR REPLACE INTO confirmations VALUES (?, ?, ?, ?, ?)''',
                     (admin_id, action, token, snapshot(conn), int(time.time()) + 600))
        return token


def consume_confirmation(conn, admin_id, action, token):
    row = conn.execute('SELECT token, snapshot, expires_at FROM confirmations WHERE admin_id=? AND action=?',
                       (admin_id, action)).fetchone()
    if not row or row[0] != token or row[1] != snapshot(conn) or row[2] < time.time():
        return False
    conn.execute('DELETE FROM confirmations WHERE admin_id=? AND action=?', (admin_id, action))
    return True


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


def draw(admin_id, token):
    with connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        if not consume_confirmation(conn, admin_id, 'draw', token):
            return []
        if conn.execute('SELECT 1 FROM users WHERE santa_for IS NOT NULL').fetchone():
            return []
        ids = [row[0] for row in conn.execute('SELECT user_id FROM users WHERE gift IS NOT NULL')]
        if len(ids) < 2:
            return []
        secrets.SystemRandom().shuffle(ids)
        conn.executemany('UPDATE users SET santa_for=? WHERE user_id=?',
                         [(ids[(i + 1) % len(ids)], user_id) for i, user_id in enumerate(ids)])
        conn.execute('UPDATE users SET notification_pending=1 WHERE santa_for IS NOT NULL')
        return ids


def assigned_ids():
    with connect() as conn:
        return [row[0] for row in conn.execute('SELECT user_id FROM users WHERE notification_pending=1')]


def mark_notified(user_id):
    with connect() as conn:
        conn.execute('UPDATE users SET notification_pending=0 WHERE user_id=?', (user_id,))


def new_game(admin_id, token):
    """Archive the current event database and clear it for a new event."""
    with connect() as conn:
        conn.execute('BEGIN IMMEDIATE')
        if not consume_confirmation(conn, admin_id, 'new_game', token):
            return None
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
            conn.execute('DELETE FROM confirmations')
        except Exception:
            backup_path.unlink(missing_ok=True)
            raise
        return backup_path


def roster():
    with connect() as conn:
        return conn.execute('SELECT username, gift IS NOT NULL FROM users ORDER BY username, user_id').fetchall()
