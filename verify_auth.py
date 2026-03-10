import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from app_factory import create_app
from database import db
from models import Account, StudentProfile, CompanyProfile, AccountRole, AccountState, BlacklistEntry, ApprovalAction
from werkzeug.security import generate_password_hash

def test_login_logic():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        # Clean up
        test_email = "test_student@college.edu"
        password = "password123"
        
        # Comprehensive cleanup
        acc = Account.query.filter_by(login_identifier=test_email).first()
        if acc:
            if acc.student_profile:
                BlacklistEntry.query.filter_by(entity_type='student', entity_id=acc.student_profile.id).delete()
                db.session.delete(acc.student_profile)
            db.session.delete(acc)
        
        company_email = "test_company@work.com"
        acc_c = Account.query.filter_by(login_identifier=company_email).first()
        if acc_c:
             if acc_c.company_profile:
                 BlacklistEntry.query.filter_by(entity_type='company', entity_id=acc_c.company_profile.id).delete()
                 db.session.delete(acc_c.company_profile)
             db.session.delete(acc_c)
        
        db.session.commit()

        # Create test student
        account = Account(
            login_identifier=test_email,
            password_hash=generate_password_hash(password),
            role=AccountRole.STUDENT.value,
            account_state=AccountState.ACTIVE.value
        )
        db.session.add(account)
        db.session.commit()
        
        profile = StudentProfile(
            account_id=account.id,
            full_name="Test Student",
            university_register_number="TEST001",
            institutional_email=test_email,
            primary_phone="1234567890"
        )
        db.session.add(profile)
        db.session.commit()
        
        # Verify account in DB
        acc_db = Account.query.filter_by(login_identifier=test_email).first()
        print(f"VERIFY: Account {acc_db.login_identifier}, Role: {acc_db.role}, State: {acc_db.account_state}")

        client = app.test_client()

        # Test Case 1: Active user
        print("Testing active user login...")
        resp = client.post("/student/login", data={"email": test_email, "password": password}, follow_redirects=False)
        print(f"DEBUG: Status: {resp.status_code}, Location: {resp.location}")
        if resp.status_code == 302 and "student/dashboard" in str(resp.location):
            print("SUCCESS: Active user logged in.")
        else:
            print(f"FAILURE: Active user login failed.")

        # Clean up
        db.session.delete(profile)
        db.session.delete(account)
        db.session.commit()

if __name__ == "__main__":
    test_login_logic()
