from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models import Account, AccountRole, AccountState, PlacementDrive, Application, db
from datetime import datetime

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
    # Get all drives ordered by ID descending (latest first)
    all_drives = PlacementDrive.query.order_by(PlacementDrive.id.desc()).all()
    return render_template("admin/drives.html", drives=all_drives)

@admin_bp.route("/approve-drive/<int:drive_id>")
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.approval_status = "Approved"
    drive.approved_at = datetime.now()
    
    db.session.commit()
    flash("Drive approved successfully", "success")
    return redirect(url_for("admin.drives"))

@admin_bp.route("/reject-drive/<int:drive_id>", methods=["POST"])
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    reason = request.form.get("rejection_reason")
    
    drive.approval_status = "Rejected"
    drive.rejection_reason = reason
    
    db.session.commit()
    flash("Drive rejected with reason", "warning")
    return redirect(url_for("admin.drives"))

@admin_bp.route("/applications")
def applications():
    # Fetch all applications with joined student and drive info
    all_apps = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template("admin/applications.html", applications=all_apps)
@admin_bp.route("/blacklisted")
def blacklisted():
    return render_template("admin/blacklisted.html", students=[])
