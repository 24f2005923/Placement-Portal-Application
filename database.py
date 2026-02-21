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
        roll_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        gender TEXT,
        dob TEXT,
        college_email TEXT UNIQUE NOT NULL,
        personal_email TEXT,
        mobile TEXT,
        alt_mobile TEXT,
        password TEXT NOT NULL,
        is_blacklisted BOOLEAN DEFAULT 0,
        blacklist_reason TEXT,
        date_blacklisted TEXT
    )
    ''')
    
    # Companies Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id_field TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        hr_contact TEXT NOT NULL,
        website TEXT,
        work_email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        company_type TEXT,
        est_year INTEGER,
        company_size TEXT,
        industry_type TEXT,
        location TEXT,
        status TEXT DEFAULT 'Pending'
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
