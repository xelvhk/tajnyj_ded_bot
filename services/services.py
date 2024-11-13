import sqlite3
import random

def start_record():
    conn = sqlite3.connect('data/santas.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE,
        username TEXT,
        santa_for INTEGER,
        gift_message TEXT,
        snowball_hits INTEGER DEFAULT 0,
        throwers TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()