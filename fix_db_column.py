import sqlite3
import os

# Path to the database
db_path = 'instance/placement_portal.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(student_applications)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns in student_applications: {columns}")
        
        if 'application_status' in columns and 'status' not in columns:
            print("Renaming 'application_status' to 'status'...")
            # SQLite 3.25.0+ supports RENAME COLUMN
            cursor.execute("ALTER TABLE student_applications RENAME COLUMN application_status TO status")
            conn.commit()
            print("Successfully renamed 'application_status' to 'status'.")
        elif 'status' in columns:
            print("'status' column already exists.")
        else:
            print("Adding 'status' column...")
            cursor.execute("ALTER TABLE student_applications ADD COLUMN status VARCHAR(50) DEFAULT 'Applied'")
            conn.commit()
            print("Successfully added 'status' column.")
            
        conn.close()
    except Exception as e:
        print(f"Error updating database: {e}")
