from database import get_db_connection

def create_dummy_company():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO companies (
                company_id_field, name, hr_contact, website, work_email, password, 
                company_type, est_year, company_size, industry_type, 
                location, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'COMP-DUMMY-101',
            'Dummy Tech Corp', 
            'John HR', 
            'https://dummytech.com', 
            'company@gmail.com', 
            'password', 
            'MNC', 
            2010, 
            '1000+', 
            'Software', 
            'Bangalore', 
            'Active'
        ))
        conn.commit()
        print("Dummy company created successfully!")

        # Create Dummy Student
        cursor.execute('''
            INSERT INTO students (
                roll_number, name, gender, dob, college_email,
                personal_email, mobile, alt_mobile, password
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '2024CS001',
            'Alex Johnson',
            'Male',
            '2002-05-15',
            'student@gmail.com',
            'alex.personal@gmail.com',
            '9876543210',
            '9876543211',
            'password'
        ))
        conn.commit()
        print("Dummy student created successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_dummy_company()
