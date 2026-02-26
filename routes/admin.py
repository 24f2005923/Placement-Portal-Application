from flask import Blueprint, render_template, redirect, url_for, session, flash
from database import db
from models import Account, AccountRole, AccountState

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
    return render_template("admin/dashboard.html", counts=counts)

@admin_bp.route("/students")
def students():
    # View all student accounts
    students = Account.query.filter_by(role=AccountRole.STUDENT).all()
    return render_template("admin/students.html", students=students)

@admin_bp.route("/students/verify/<int:account_id>/<action>", methods=["POST"])
def verify_student(account_id, action):
    account = Account.query.get(account_id)
    if account:
        if action == "approve":
            account.account_state = AccountState.ACTIVE
        elif action == "reject":
            account.account_state = AccountState.REJECTED
        db.session.commit()
    return redirect(url_for("admin.students"))

@admin_bp.route("/companies")
def companies():
    # View all company accounts
    accounts = Account.query.filter_by(role=AccountRole.COMPANY).all()
    company_profiles = [acc.company_profile for acc in accounts if acc.company_profile]
    return render_template("admin/companies.html", companies=company_profiles)

@admin_bp.route("/companies/verify/<int:account_id>/<action>", methods=["POST"])
def verify_company(account_id, action):
    account = Account.query.get(account_id)
    if account:
        if action == "approve":
            account.account_state = AccountState.ACTIVE
        elif action == "reject":
            account.account_state = AccountState.REJECTED
        db.session.commit()
    return redirect(url_for("admin.companies"))

@admin_bp.route("/drives")
def drives():
    return render_template("admin/drives.html", drives=[])

@admin_bp.route("/blacklisted")
def blacklisted():
    return render_template("admin/blacklisted.html", students=[])
