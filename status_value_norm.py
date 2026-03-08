from app_factory import create_app
from database import db
from sqlalchemy import text

def fix_enum_case():
    app = create_app()
    with app.app_context():
        print("Starting data fix for Enum case sensitivity...")
        
        # Mapping Title Case -> Uppercase (Enum member names)
        # DriveStatus: PENDING, APPROVED, REJECTED
        # ApplicationStatus: APPLIED, SHORTLISTED, SELECTED, REJECTED
        
        fixes = [
            ("UPDATE placement_drives SET approval_status = 'APPROVED' WHERE approval_status = 'Approved'"),
            ("UPDATE placement_drives SET approval_status = 'REJECTED' WHERE approval_status = 'Rejected'"),
            ("UPDATE placement_drives SET approval_status = 'PENDING' WHERE approval_status = 'Pending'"),
            
            ("UPDATE student_applications SET status = 'APPLIED' WHERE status = 'Applied'"),
            ("UPDATE student_applications SET status = 'SHORTLISTED' WHERE status = 'Shortlisted'"),
            ("UPDATE student_applications SET status = 'SELECTED' WHERE status = 'Selected'"),
            ("UPDATE student_applications SET status = 'REJECTED' WHERE status = 'Rejected'")
        ]
        
        try:
            for sql in fixes:
                result = db.session.execute(text(sql))
                print(f"Executed: {sql} | Rows affected: {result.rowcount}")
            
            db.session.commit()
            print("Data fix completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during data fix: {e}")

if __name__ == "__main__":
    fix_enum_case()
