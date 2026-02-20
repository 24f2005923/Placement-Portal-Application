import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "placement_portal.db")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Students Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        is_blacklisted BOOLEAN DEFAULT 0,
        blacklist_reason TEXT,
        date_blacklisted TEXT
    )
    ''')
    
    # Companies Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        industry TEXT NOT NULL,
        contact_person TEXT NOT NULL,
        status TEXT DEFAULT 'Active'
    )
    ''')
    
    # Drives Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company_id INTEGER,
        date TEXT NOT NULL,
        status TEXT DEFAULT 'Open',
        FOREIGN KEY (company_id) REFERENCES companies (id)
    )
    ''')
    
    # Applications Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        drive_id INTEGER,
        status TEXT DEFAULT 'Pending',
        date_applied TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (drive_id) REFERENCES drives (id)
    )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database Initialized!")
