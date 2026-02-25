from flask import Blueprint, render_template, redirect, url_for, session, flash
from database import db
from models import Account, AccountRole, AccountState
from services.account_service import verify_student_account

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.before_request
def admin_required():
    if session.get("role") != "admin":
        return redirect(url_for("auth.admin_login"))

@admin_bp.route("/dashboard")
def dashboard():
    # Placeholder for dashboard counts
    counts = {
        "students": Account.query.filter_by(role=AccountRole.STUDENT).count(),
        # "companies": Account.query.filter_by(role=AccountRole.COMPANY).count(),
        # "drives": Drive.query.count()
    }
    return render_template("admin_dashboard.html", counts=counts)

@admin_bp.route("/students")
def students():
    # View all non-pending students
    students = Account.query.filter(
        Account.role == AccountRole.STUDENT,
        Account.account_state != AccountState.PENDING_VERIFICATION
    ).all()
    return render_template("admin_students.html", students=students)

@admin_bp.route("/students/pending")
def pending_students():
    # View only students that are PENDING_VERIFICATION
    pending_students = Account.query.filter_by(
        role=AccountRole.STUDENT,
        account_state=AccountState.PENDING_VERIFICATION
    ).all()
    return render_template("admin_students.html", students=pending_students, is_pending=True)

@admin_bp.route("/students/verify/<int:account_id>/<action>", methods=["POST"])
def verify_student(account_id, action):
    admin_id = session.get("account_id")
    try:
        verify_student_account(admin_id, account_id, action)
        flash(f"Student account {action}ed successfully.", "success")
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
    return redirect(url_for("admin.pending_students"))

# Add placeholders for other admin routes coming from app.py
@admin_bp.route("/companies")
def companies():
    return render_template("admin_companies.html", companies=[])

@admin_bp.route("/drives")
def drives():
    return render_template("admin_drives.html", drives=[])

@admin_bp.route("/blacklisted")
def blacklisted():
    return render_template("admin_blacklisted.html", students=[])
