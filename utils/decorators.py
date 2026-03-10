from functools import wraps
from flask import session, redirect, url_for, flash
from models import Account, AccountState

def active_account_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        account_id = session.get("account_id")
        
        def safe_redirect():
            """Determine safest login page based on user role or fallback."""
            role = session.get("role")
            if role == AccountRole.ADMIN.value:
                return redirect(url_for("auth.admin_login"))
            elif role == AccountRole.STUDENT.value:
                return redirect(url_for("auth.student_login"))
            elif role == AccountRole.COMPANY.value:
                return redirect(url_for("auth.company_login"))
            
            # If no specific role is found, fallback to index
            return redirect(url_for("main.index"))

        if not account_id:
            return safe_redirect()
            
        account = Account.query.get(account_id)
        if not account:
            session.clear()
            return safe_redirect()
            
        if account.account_state == AccountState.PENDING_VERIFICATION.value:
            flash("Your account is pending admin verification. Please wait.", "warning")
            return redirect(url_for("main.index"))
            
        if account.account_state == AccountState.REJECTED.value:
            flash("Your account registration was rejected by the admin.", "danger")
            session.clear()
            return safe_redirect()
            
        if account.account_state == AccountState.SUSPENDED.value:
            flash("Your account has been suspended.", "danger")
            session.clear()
            return safe_redirect()
            
        if account.account_state != AccountState.ACTIVE.value:
            flash("Access denied. Your account is not active.", "danger")
            return redirect(url_for("main.index"))
            
        return f(*args, **kwargs)
    return decorated_function
