import sqlite3
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()
        
    def _get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def _init_db(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    headline TEXT,
                    company TEXT,
                    topic TEXT,
                    geography TEXT,
                    source TEXT,
                    url TEXT UNIQUE,
                    key_facts TEXT,
                    strategic_theme TEXT
                )
            ''')
            conn.commit()
            
    def insert_story(self, date, headline, company, topic, geography, source, url, key_facts, strategic_theme):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO stories (date, headline, company, topic, geography, source, url, key_facts, strategic_theme)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (date, headline, company, topic, geography, source, url, key_facts, strategic_theme))
                conn.commit()
        except Exception as e:
            logging.error(f"Error inserting story into DB: {e}")
            
    def get_recent_stories(self, days=7):
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM stories WHERE date >= ? ORDER BY date DESC
                ''', (cutoff_date,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Error fetching recent stories: {e}")
            return []
            
    def is_url_processed(self, url):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM stories WHERE url = ?', (url,))
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Error checking URL in DB: {e}")
            return False
