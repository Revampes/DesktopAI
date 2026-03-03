import sqlite3
import os
import shutil

DB_PATH = os.path.join(os.path.dirname(__file__), 'assistant.db')
MUSIC_DIR = os.path.join(os.path.dirname(__file__), 'music_library')

class DatabaseManager:
    def __init__(self):
        os.makedirs(MUSIC_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Calendar Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date_str TEXT NOT NULL,
                time_str TEXT NOT NULL,
                notify INTEGER DEFAULT 0
            )
        ''')
        
        # Music Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS music (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                file_path TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()

    # --- Music Methods ---
    def add_song(self, title, author, source_path):
        filename = os.path.basename(source_path)
        dest_path = os.path.join(MUSIC_DIR, filename)
        
        # Copy to local library if not there
        if source_path != dest_path:
            shutil.copy2(source_path, dest_path)
            
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO music (title, author, file_path) VALUES (?, ?, ?)", 
                       (title, author, dest_path))
        self.conn.commit()
        return True

    def get_all_songs(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, author, file_path FROM music")
        return cursor.fetchall()
        
    def find_song_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT file_path FROM music WHERE title LIKE ?", (f"%{name}%",))
        result = cursor.fetchone()
        return result[0] if result else None

    # --- Calendar Methods ---
    def add_schedule(self, title, date_str, time_str, notify=0):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO calendar (title, date_str, time_str, notify) VALUES (?, ?, ?, ?)",
                       (title, date_str, time_str, notify))
        self.conn.commit()
        return True
        
    def get_all_schedules(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, date_str, time_str, notify FROM calendar ORDER BY date_str, time_str")
        return cursor.fetchall()

db = DatabaseManager()
