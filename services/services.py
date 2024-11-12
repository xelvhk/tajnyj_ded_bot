import sqlite3
import random

def start_record():
    conn = sqlite3.connect('data/santas.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        gift TEXT,
        address_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()
