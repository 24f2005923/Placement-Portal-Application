from flask import session, g
from markupsafe import Markup
from models import StudentProfile, CompanyProfile
from datetime import datetime

def get_current_student_profile():
    """Return the StudentProfile for the currently logged-in student account.
    Uses flask.g to cache the profile for the duration of the request.
    """
    if 'current_student_profile' not in g:
        account_id = session.get("account_id")
        if account_id:
            g.current_student_profile = StudentProfile.query.filter_by(account_id=account_id).first()
        else:
            g.current_student_profile = None
    return g.current_student_profile


def get_current_company_profile():
    """Return the CompanyProfile for the currently logged-in company account.
    Uses flask.g to cache the profile for the duration of the request.
    """
    if 'current_company_profile' not in g:
        account_id = session.get("account_id")
        if account_id:
            g.current_company_profile = CompanyProfile.query.filter_by(account_id=account_id).first()
        else:
            g.current_company_profile = None
    return g.current_company_profile


def format_drive_date(value):
    # organic date formatting for drive deadlines
    if not value:
        return "N/A"
    return value.strftime('%d %b, %Y')

def status_badge(status):
    # dynamic component for consistent status visualization
    if not status:
        return Markup('<span class="badge bg-light text-muted border rounded-pill">Unknown</span>')
    
    # support both Enum and string, normalizing underscores
    status_str = str(status.value) if hasattr(status, 'value') else str(status)
    normalized = status_str.replace('_', ' ').title()
    
    mapping = {
        'Applied': 'bg-primary-subtle text-primary',
        'Shortlisted': 'bg-warning-subtle text-warning',
        'Selected': 'bg-success-subtle text-success',
        'Rejected': 'bg-danger-subtle text-danger',
        'Approved': 'bg-success-subtle text-success',
        'Pending': 'bg-warning-subtle text-warning',
        'Active': 'bg-success-subtle text-success',
        'Pending Verification': 'bg-warning-subtle text-warning',
        'Suspended': 'bg-dark-subtle text-dark'
    }
    
    cls = mapping.get(normalized, 'bg-light text-muted')
    return Markup(f'<span class="badge {cls} border px-3 py-2 rounded-pill">{normalized}</span>')

def init_filters(app):
    app.jinja_env.filters['format_drive_date'] = format_drive_date
    app.jinja_env.filters['status_badge'] = status_badge
