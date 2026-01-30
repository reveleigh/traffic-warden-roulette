import sqlite3
import datetime

DB_FILE = "game_data.db"

def init_db():
    """
    Initialises the database tables if they do not exist.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # Create High Scores Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    date_achieved TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            print("Database initialised successfully.")
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def save_score(name, score):
    """Saves a new score to the database."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO high_scores (name, score) VALUES (?, ?)", (name, score))
            conn.commit()
            print(f"Score {score} for {name} saved to database.")
    except sqlite3.Error as e:
        print(f"Error saving score: {e}")

def get_top_scores(limit=50):
    """Retrieves the top N high scores."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, score, date_achieved 
                FROM high_scores 
                ORDER BY score DESC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error retrieving scores: {e}")
        return []
