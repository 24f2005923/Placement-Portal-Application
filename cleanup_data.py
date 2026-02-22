from database import get_db_connection

def cleanup_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Clear all applications and drives (these are dummy data)
        cursor.execute('DELETE FROM applications')
        cursor.execute('DELETE FROM drives')
        
        # 2. Clear students but preserve the main login credentials
        # We delete everyone who ISN'T our main dummy student
        cursor.execute("DELETE FROM students WHERE college_email != 'student@gmail.com'")
        
        # 3. Clear companies but preserve the main login credentials
        cursor.execute("DELETE FROM companies WHERE work_email != 'company@gmail.com'")
        
        # 4. Ensure the main credentials exist if they were missing
        # Check student
        student = cursor.execute("SELECT id FROM students WHERE college_email = 'student@gmail.com'").fetchone()
        if not student:
            cursor.execute('''
                INSERT INTO students (
                    roll_number, name, gender, dob, college_email,
                    personal_email, mobile, alt_mobile, password
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('2024CS001', 'Alex Johnson', 'Male', '2002-05-15', 'student@gmail.com', 
                  'alex.personal@gmail.com', '9876543210', '9876543211', 'password'))
            print("Base student account restored.")

        # Check company
        company = cursor.execute("SELECT id FROM companies WHERE work_email = 'company@gmail.com'").fetchone()
        if not company:
            cursor.execute('''
                INSERT INTO companies (
                    company_id_field, name, hr_contact, website, work_email, password, 
                    company_type, est_year, company_size, industry_type, 
                    location, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('COMP-DUMMY-101', 'Dummy Tech Corp', 'John HR', 'https://dummytech.com', 
                  'company@gmail.com', 'password', 'MNC', 2010, '1000+', 'Software', 'Bangalore', 'Active'))
            print("Base company account restored.")

        conn.commit()
        print("Database cleaned up successfully! All dummy data removed except base login credentials.")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_data()
