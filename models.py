from database import get_db_connection

class Student:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        students = conn.execute('SELECT * FROM students').fetchall()
        conn.close()
        return students

    @staticmethod
    def get_blacklisted():
        conn = get_db_connection()
        students = conn.execute('SELECT * FROM students WHERE is_blacklisted = 1').fetchall()
        conn.close()
        return students

class Company:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        companies = conn.execute('SELECT * FROM companies').fetchall()
        conn.close()
        return companies

class Drive:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        drives = conn.execute('''
            SELECT drives.*, companies.name as company_name 
            FROM drives 
            JOIN companies ON drives.company_id = companies.id
        ''').fetchall()
        conn.close()
        return drives

class Application:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        applications = conn.execute('''
            SELECT applications.*, students.name as student_name, drives.title as drive_title 
            FROM applications 
            JOIN students ON applications.student_id = students.id
            JOIN drives ON applications.drive_id = drives.id
        ''').fetchall()
        conn.close()
        return applications

def get_counts():
    conn = get_db_connection()
    counts = {
        'students': conn.execute('SELECT COUNT(*) FROM students').fetchone()[0],
        'companies': conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0],
        'drives': conn.execute('SELECT COUNT(*) FROM drives').fetchone()[0],
        'applications': conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
    }
    conn.close()
    return counts
