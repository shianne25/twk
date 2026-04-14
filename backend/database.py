import sqlite3
import os

# Build a path to data/slang_db.sqlite relative to this file
# Hint: use os.path to go one folder up from backend/, then into data/
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'slang_db.sqlite')

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def create_table():
    """Create the mappings table if it doesn't already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Write the CREATE TABLE IF NOT EXISTS SQL here
    # Columns you need: id, formal_phrase, slang_term, definition
    # Look at the schema in your PRD for the types

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            formal_phrase TEXT NOT NULL,
            slang_term TEXT NOT NULL,
            definition TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def seed_data():
    """Insert starter phrases — skip any that already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    phrases = [
        ("great job" , "ate" , "Slang term for 'great job' or 'well done'"),
        ("laugh out loud", "LOL", "Short form for 'laugh out loud', used to indicate something is funny"),
        ("win", "W", "Short form for 'win', used to indicate success or victory"),
        ("mediocre", "mid" , "Slang term for something that is average or not impressive"),
        ("stay in bed all day", "bedrot", "Slang term for the act of staying in bed all day, often used humorously to describe laziness or relaxation"),
        ("i'm so angry", "i'm crashing out", "Slang term for being extremely angry or frustrated, often used to express intense emotions"),
        ("it's over" , "it's cooked", "Slang term for something that is finished, ruined, or no longer viable"),
        ("i'm tired", "i'm dead", "Slang term for being extremely tired or exhausted, often used humorously to express fatigue"),
        ("that's too much" ,"that's OD" , "Slang term for something that is excessive or overwhelming, often used to indicate that something is over the top"),
        ("original", "day 1", "Slang for someone who has been around since the beginning of a trend, movement, or community, often used to indicate loyalty or authenticity"),
        ("old", "unc" , "Slang term for something that is old or outdated, often used humorously to describe something that is no longer relevant or fashionable"),
        ("charisma", "rizz", "Slang term for charisma or charm, often used to describe someone who has a magnetic personality or is particularly attractive"),
    ]
    
    # INSERT OR IGNORE so re-running the script doesn't duplicate rows
    cursor.executemany("""
        INSERT OR IGNORE INTO mappings (formal_phrase, slang_term, definition)
        VALUES (?,?,?)
    """, phrases)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    seed_data()
    print("Database ready.")