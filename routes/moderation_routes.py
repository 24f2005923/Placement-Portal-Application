from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models import Account, AccountRole, AccountState, PlacementDrive, StudentApplication, db, DriveStatus, ApplicationStatus, BlacklistEntry, StudentProfile, CompanyProfile
from datetime import datetime

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.before_request
def admin_required():
    if session.get("role") != "admin":
        return redirect(url_for("auth.admin_login"))

@admin_bp.route("/dashboard", endpoint="dashboard")
def render_moderation_hub():
    counts = {
        "students": Account.query.filter_by(role=AccountRole.STUDENT.value).count(),
        "companies": Account.query.filter_by(role=AccountRole.COMPANY.value).count(),
        "drives": PlacementDrive.query.count(),
        "applications": StudentApplication.query.count(),
    }
    return render_template("admin/dashboard.html", counts=counts)

@admin_bp.route("/students", endpoint="students")
def list_registered_students():
    search_query = request.args.get('q', '').strip()
    query = Account.query.filter_by(role=AccountRole.STUDENT.value)
    
    if search_query:
        from models import StudentProfile
        query = query.join(StudentProfile).filter(
            db.or_(
                StudentProfile.full_name.ilike(f"%{search_query}%"),
                StudentProfile.university_register_number.ilike(f"%{search_query}%"),
                StudentProfile.institutional_email.ilike(f"%{search_query}%"),
                Account.login_identifier.ilike(f"%{search_query}%")
            )
        )
    
    students = query.all()
    return render_template("admin/students.html", students=students, search_query=search_query)

@admin_bp.route("/students/verify/<int:account_id>/<action>", methods=["POST"], endpoint="verify_student")
def process_student_verification(account_id, action):
    account = Account.query.get(account_id)
    if account:
        account.account_state = AccountState.ACTIVE.value if action == "approve" else AccountState.REJECTED.value
        db.session.commit()
    return redirect(url_for("admin.students"))

@admin_bp.route("/companies", endpoint="companies")
def list_corporate_partners():
    search_query = request.args.get('q', '').strip()
    from models import CompanyProfile
    query = CompanyProfile.query.join(Account).filter(Account.role == AccountRole.COMPANY.value)
    
    if search_query:
        query = query.filter(
            db.or_(
                CompanyProfile.name.ilike(f"%{search_query}%"),
                CompanyProfile.work_email.ilike(f"%{search_query}%"),
                CompanyProfile.industry_type.ilike(f"%{search_query}%")
            )
        )
    
    company_profiles = query.all()
    return render_template("admin/companies.html", companies=company_profiles, search_query=search_query)

@admin_bp.route("/companies/verify/<int:account_id>/<action>", methods=["POST"], endpoint="verify_company")
def process_company_verification(account_id, action):
    account = Account.query.get(account_id)
    if account:
        account.account_state = AccountState.ACTIVE.value if action == "approve" else AccountState.REJECTED.value
        db.session.commit()
    return redirect(url_for("admin.companies"))

@admin_bp.route("/drives", endpoint="drives")
def browse_recruitment_drives():
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
    # Filter by type if provided
    filter_type = request.args.get('type')
    query = BlacklistEntry.query
    if filter_type:
        query = query.filter_by(entity_type=filter_type)
    
    blacklisted_items = query.order_by(BlacklistEntry.blacklisted_at.desc()).all()
    
    # Enrich blacklisted items with names/identifiers
    for item in blacklisted_items:
        item.display_name = "Unknown"
        if item.entity_type == 'student':
            student = StudentProfile.query.get(item.entity_id)
            if student: item.display_name = student.full_name
        elif item.entity_type == 'company':
            company = CompanyProfile.query.get(item.entity_id)
            if company: item.display_name = company.name
        elif item.entity_type == 'drive':
            drive = PlacementDrive.query.get(item.entity_id)
            if drive: item.display_name = drive.job_title
        elif item.entity_type == 'application':
            app = StudentApplication.query.get(item.entity_id)
            if app: item.display_name = f"{app.student.full_name} - {app.drive.job_title}"

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
        blacklisted_items=blacklisted_items,
        rejected_students=rejected_students,
        rejected_companies=rejected_companies,
        rejected_drives=rejected_drives,
        rejected_apps=rejected_apps,
        filter_type=filter_type
    )

@admin_bp.route("/blacklist/<entity_type>/<int:entity_id>", methods=["POST"], endpoint="blacklist_entity")
def blacklist_entity(entity_type, entity_id):
    reason = request.form.get("reason", "No reason provided")
    admin_id = session.get("account_id") # Fixed from user_id to account_id
    
    # Check if already blacklisted
    existing = BlacklistEntry.query.filter_by(entity_type=entity_type, entity_id=entity_id).first()
    if existing:
        flash(f"This {entity_type} is already blacklisted.", "warning")
    else:
        new_entry = BlacklistEntry(
            entity_type=entity_type,
            entity_id=entity_id,
            reason=reason,
            admin_id=admin_id
        )
        db.session.add(new_entry)
        db.session.commit()
        flash(f"{entity_type.capitalize()} has been blacklisted.", "danger")
        
    return redirect(url_for("admin.blacklisted"))

@admin_bp.route("/unblacklist/<int:entry_id>", methods=["POST"], endpoint="unblacklist_entity")
def unblacklist_entity(entry_id):
    entry = BlacklistEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Entity has been restored from blacklist.", "success")
    return redirect(url_for("admin.blacklisted"))
