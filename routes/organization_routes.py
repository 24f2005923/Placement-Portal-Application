from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from utils.decorators import active_account_required
from utils.helpers import get_current_company_profile
from models import CompanyProfile, PlacementDrive, StudentApplication, db, DriveStatus, ApplicationStatus
from datetime import datetime
import random
import string

company_bp = Blueprint("company", __name__, url_prefix="/company")

def generate_drive_id():
    # helper to build a unique drive identifier
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"DRV-{date_str}-{random_str}"

@company_bp.before_request
def company_required():
    # gotta make sure it's a company user and not some random student or admin
    if session.get("role") != "company":
        return redirect(url_for("auth.company_login"))

@company_bp.route("/dashboard", endpoint="dashboard")
@active_account_required
def hiring_partner_overview():
    profile = get_current_company_profile()
    if not profile: return redirect(url_for("auth.company_login"))

    drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
    drive_ids = [d.id for d in drives]
    
    # temporary guard for empty drives
    active_count = PlacementDrive.query.filter_by(company_id=profile.id, approval_status=DriveStatus.APPROVED).count()
    total_apps = StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids)).count() if drive_ids else 0
    
    # status tracking breakdown
    status_counts = {
        'Applied': StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids), StudentApplication.status == ApplicationStatus.APPLIED).count() if drive_ids else 0,
        'Shortlisted': StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids), StudentApplication.status == ApplicationStatus.SHORTLISTED).count() if drive_ids else 0,
        'Selected': StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids), StudentApplication.status == ApplicationStatus.SELECTED).count() if drive_ids else 0,
        'Rejected': StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids), StudentApplication.status == ApplicationStatus.REJECTED).count() if drive_ids else 0
    }
    
    recent = PlacementDrive.query.filter_by(company_id=profile.id).order_by(PlacementDrive.created_at.desc()).limit(5).all()

    return render_template("company/dashboard.html", company_name=profile.name, 
                           active_drives=active_count, total_apps=total_apps, 
                           pending_review=status_counts['Applied'], hired=status_counts['Selected'], 
                           status_counts=status_counts, recent_drives=recent)

@company_bp.route("/create-drive", methods=["GET", "POST"], endpoint="create_drive")
@active_account_required
def initiate_recruitment_drive():
    profile = get_current_company_profile()
    
    if not profile:
        flash("Company profile not found.", "danger")
        return redirect(url_for("company.dashboard"))

    if request.method == "POST":
        try:
            # persisting drive details to the catalog
            job_title = request.form.get("job_title") 
            job_description = request.form.get("job_description")
            eligibility = request.form.get("eligibility_criteria") 
            job_location = request.form.get("job_location")
            package = request.form.get("package_amount") 
            deadline_str = request.form.get("application_deadline")

            new_drive = PlacementDrive(
                company_id=profile.id,
                job_title=job_title,
                job_description=job_description,
                eligibility_criteria=eligibility,
                job_location=job_location or "On-Site",
                package_amount=package,
                application_deadline=datetime.strptime(deadline_str, '%Y-%m-%d'),
                approval_status=DriveStatus.PENDING
            )
            
            db.session.add(new_drive)
            db.session.commit()
            flash("Placement drive submitted successfully and is pending approval.", "success")
            return redirect(url_for("company.create_drive"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating drive: {str(e)}", "danger")

    company_name = profile.name
    generated_drive_id = generate_drive_id()
    
    existing_drives = PlacementDrive.query.filter_by(company_id=profile.id).order_by(PlacementDrive.created_at.desc()).all()
    
    return render_template("company/create_drive.html", 
                           company_name=company_name, 
                           company_id=profile.company_id_field,
                           drive_id=generated_drive_id,
                           drives=existing_drives)

@company_bp.route("/my-drives", endpoint="my_drives")
@active_account_required
def personal_drive_catalog():
    profile = get_current_company_profile()
    company_name = profile.name if profile else "Company User"
    return render_template("company/my_drives.html", drives=[], company_name=company_name)

@company_bp.route("/applications", endpoint="applications")
@active_account_required
def track_received_applications():
    profile = get_current_company_profile()
    company_name = profile.name if profile else "Company User"
    search_query = request.args.get('search', '').strip()
    
    apps = []
    if profile:
        from models import StudentProfile, PlacementDrive
        
        query = StudentApplication.query.join(PlacementDrive).filter(PlacementDrive.company_id == profile.id)
        
        if search_query:
            query = query.join(StudentProfile).filter(
                db.or_(
                    StudentProfile.full_name.ilike(f"%{search_query}%"),
                    StudentProfile.university_register_number.ilike(f"%{search_query}%"),
                    PlacementDrive.job_title.ilike(f"%{search_query}%")
                )
            )
        
        apps = query.all()
            
    return render_template("company/applications.html", applications=apps, company_name=company_name, search_query=search_query)

@company_bp.route("/shortlisted", endpoint="shortlisted_students")
@active_account_required
def view_shortlisted_candidates():
    profile = get_current_company_profile()
    company_name = profile.name if profile else "Company User"
    
    shortlisted = []
    if profile:
        drive_ids = [d.id for d in PlacementDrive.query.filter_by(company_id=profile.id).all()]
        if drive_ids:
            shortlisted = StudentApplication.query.filter(
                StudentApplication.drive_id.in_(drive_ids),
                StudentApplication.status == ApplicationStatus.SHORTLISTED
            ).all()
            
    return render_template("company/shortlisted.html", students=shortlisted, company_name=company_name)

@company_bp.route("/selected", endpoint="selected_students")
@active_account_required
def view_final_selections():
    profile = get_current_company_profile()
    company_name = profile.name if profile else "Company User"
    
    selected = []
    if profile:
        drive_ids = [d.id for d in PlacementDrive.query.filter_by(company_id=profile.id).all()]
        if drive_ids:
            selected = StudentApplication.query.filter(
                StudentApplication.drive_id.in_(drive_ids),
                StudentApplication.status == ApplicationStatus.SELECTED
            ).all()
            
    return render_template("company/selected.html", students=selected, company_name=company_name)

@company_bp.route("/profile", endpoint="profile")
@active_account_required
def manage_organization_profile():
    profile = get_current_company_profile()
    
    company_data = None
    if profile:
        company_data = {
            "name": profile.name,
            "company_id": profile.company_id_field,
            "website": profile.website_url,
            "industry": profile.industry_type,
            "location": profile.location,
            "hr_contact": profile.hr_contact,
            "email": profile.work_email
        }
    
    company_name = profile.name if profile else "Company User"
    return render_template("company/profile.html", company_name=company_name, company=company_data)
