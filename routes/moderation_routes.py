from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models import Account, AccountRole, AccountState, PlacementDrive, StudentApplication, db, DriveStatus, ApplicationStatus
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# --- ADMIN ACCESS GUARD ---
@admin_bp.before_request
def admin_required():
    # checking if someone is trying to sneak in without proper admin role
    if session.get("role") != "admin":
        return redirect(url_for("auth.admin_login"))

@admin_bp.route("/dashboard", endpoint="dashboard")
def render_moderation_hub():
    # just a quick way to get the big numbers for the hub
    counts = {
        "students": Account.query.filter_by(role=AccountRole.STUDENT.value).count(),
        "companies": Account.query.filter_by(role=AccountRole.COMPANY.value).count(),
        "drives": PlacementDrive.query.count(),
        "applications": StudentApplication.query.count(),
    }
    return render_template("admin/dashboard.html", counts=counts)

@admin_bp.route("/students", endpoint="students")
def list_registered_students():
    # Fetching students awaiting or already verified
    students = Account.query.filter_by(role=AccountRole.STUDENT.value).all()
    return render_template("admin/students.html", students=students)

@admin_bp.route("/students/verify/<int:account_id>/<action>", methods=["POST"], endpoint="verify_student")
def process_student_verification(account_id, action):
    account = Account.query.get(account_id)
    if account:
        # Binary state toggle: approve/reject
        account.account_state = AccountState.ACTIVE.value if action == "approve" else AccountState.REJECTED.value
        db.session.commit()
    return redirect(url_for("admin.students"))

@admin_bp.route("/companies", endpoint="companies")
def list_corporate_partners():
    # Organization accounts and their active profiles
    accounts = Account.query.filter_by(role=AccountRole.COMPANY.value).all()
    company_profiles = [acc.company_profile for acc in accounts if acc.company_profile]
    return render_template("admin/companies.html", companies=company_profiles)

@admin_bp.route("/companies/verify/<int:account_id>/<action>", methods=["POST"], endpoint="verify_company")
def process_company_verification(account_id, action):
    account = Account.query.get(account_id)
    if account:
        # Handle partner onboarding status
        account.account_state = AccountState.ACTIVE.value if action == "approve" else AccountState.REJECTED.value
        db.session.commit()
    return redirect(url_for("admin.companies"))

@admin_bp.route("/drives", endpoint="drives")
def browse_recruitment_drives():
    # Centralized drive management search
    search_query = request.args.get('search', '').strip()
    query = PlacementDrive.query
    
    if search_query:
        query = query.filter(
            db.or_(
                PlacementDrive.job_title.ilike(f"%{search_query}%"),
                PlacementDrive.job_location.ilike(f"%{search_query}%")
            )
        )
    
    all_drives = query.order_by(PlacementDrive.id.desc()).all()
    return render_template("admin/drives.html", drives=all_drives, search_query=search_query)

@admin_bp.route("/approve-drive/<int:drive_id>", methods=["POST"], endpoint="approve_drive")
def validate_drive_workflow(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.approval_status = DriveStatus.APPROVED
    
    db.session.commit()
    flash("Drive approved successfully", "success")
    return redirect(url_for("admin.drives"))

@admin_bp.route("/reject-drive/<int:drive_id>", methods=["POST"], endpoint="reject_drive")
def decline_drive_workflow(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    reason = request.form.get("rejection_reason")
    
    drive.approval_status = DriveStatus.REJECTED
    drive.rejection_reason = reason
    
    db.session.commit()
    flash("Drive rejected with reason", "warning")
    return redirect(url_for("admin.drives"))

@admin_bp.route("/applications", endpoint="applications")
def inspect_student_applications():
    search_query = request.args.get('search', '').strip()
    query = StudentApplication.query
    
    if search_query:
        from models import StudentProfile, PlacementDrive, CompanyProfile
        query = query.join(StudentProfile).join(PlacementDrive).join(CompanyProfile).filter(
            db.or_(
                StudentProfile.full_name.ilike(f"%{search_query}%"),
                StudentProfile.university_register_number.ilike(f"%{search_query}%"),
                PlacementDrive.job_title.ilike(f"%{search_query}%"),
                CompanyProfile.name.ilike(f"%{search_query}%")
            )
        )
    
    all_apps = query.order_by(StudentApplication.applied_at.desc()).all()
    return render_template("admin/applications.html", applications=all_apps, search_query=search_query)

@admin_bp.route("/blacklisted", endpoint="blacklisted")
def view_restricted_entities():
    from models import CompanyProfile, StudentProfile
    # Gathering data for restricted access logs
    rejected_students = Account.query.filter_by(
        role=AccountRole.STUDENT.value, account_state=AccountState.REJECTED.value
    ).all()
    rejected_company_accounts = Account.query.filter_by(
        role=AccountRole.COMPANY.value, account_state=AccountState.REJECTED.value
    ).all()
    rejected_companies = [acc.company_profile for acc in rejected_company_accounts if acc.company_profile]
    rejected_drives = PlacementDrive.query.filter_by(approval_status=DriveStatus.REJECTED).all()
    rejected_apps = StudentApplication.query.filter_by(status=ApplicationStatus.REJECTED).all()

    return render_template(
        "admin/blacklisted.html",
        rejected_students=rejected_students,
        rejected_companies=rejected_companies,
        rejected_drives=rejected_drives,
        rejected_apps=rejected_apps
    )
