from flask import session
from models import StudentProfile, CompanyProfile


def get_current_student_profile():
    """Return the StudentProfile for the currently logged-in student account.

    Reads ``account_id`` from the Flask session and returns the matching
    StudentProfile row, or None if no profile exists yet.
    """
    account_id = session.get("account_id")
    return StudentProfile.query.filter_by(account_id=account_id).first()


def get_current_company_profile():
    """Return the CompanyProfile for the currently logged-in company account.

    Reads ``account_id`` from the Flask session and returns the matching
    CompanyProfile row, or None if no profile exists yet.
    """
    account_id = session.get("account_id")
    return CompanyProfile.query.filter_by(account_id=account_id).first()
