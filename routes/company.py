from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from utils.decorators import active_account_required
from models import CompanyProfile, PlacementDrive, StudentApplication, db
from datetime import datetime
import random
import string

company_bp = Blueprint("company", __name__, url_prefix="/company")

def generate_drive_id():
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"DRV-{date_str}-{random_str}"

@company_bp.before_request
def company_required():
    if session.get("role") != "company":
        return redirect(url_for("auth.company_login"))

@company_bp.route("/dashboard")
@active_account_required
def dashboard():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    if not profile: return redirect(url_for("auth.company_login"))

    drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
    drive_ids = [d.id for d in drives]
    
    active_count = PlacementDrive.query.filter_by(company_id=profile.id, approval_status='Approved').count()
    total_apps = StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids)).count() if drive_ids else 0
    pending = StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids), StudentApplication.status == 'Applied').count() if drive_ids else 0
    hired = StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids), StudentApplication.status == 'Selected').count() if drive_ids else 0
    recent = PlacementDrive.query.filter_by(company_id=profile.id).order_by(PlacementDrive.created_at.desc()).limit(5).all()

    return render_template("company/dashboard.html", company_name=profile.name, 
                           active_drives=active_count, total_apps=total_apps, 
                           pending_review=pending, hired=hired, recent_drives=recent)

@company_bp.route("/create-drive", methods=["GET", "POST"])
@active_account_required
def create_drive():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    
    if not profile:
        flash("Company profile not found.", "danger")
        return redirect(url_for("company.dashboard"))

    if request.method == "POST":
        try:
            # Support both new and old form layouts for safety
            job_title = request.form.get("job_title") or request.form.get("title")
            job_description = request.form.get("job_description")
            eligibility = request.form.get("eligibility_criteria") or request.form.get("eligibility_cgpa")
            job_location = request.form.get("job_location")
            package = request.form.get("package_amount") or request.form.get("salary_package")
            deadline_str = request.form.get("application_deadline")

            new_drive = PlacementDrive(
                company_id=profile.id,
                job_title=job_title,
                job_description=job_description,
                eligibility_criteria=eligibility,
                job_location=job_location or "On-Site",
                package_amount=package,
                application_deadline=datetime.strptime(deadline_str, '%Y-%m-%d'),
                approval_status="Pending"
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
    
    # Fetch all drives created by this company
    existing_drives = PlacementDrive.query.filter_by(company_id=profile.id).order_by(PlacementDrive.created_at.desc()).all()
    
    return render_template("company/create_drive.html", 
                           company_name=company_name, 
                           company_id=profile.company_id_field,
                           drive_id=generated_drive_id,
                           drives=existing_drives)

@company_bp.route("/my-drives")
@active_account_required
def my_drives():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    company_name = profile.name if profile else "Company User"
    return render_template("company/my_drives.html", drives=[], company_name=company_name)

@company_bp.route("/applications")
@active_account_required
def applications():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    company_name = profile.name if profile else "Company User"
    
    apps = []
    if profile:
        # Get all drives for this company
        drive_ids = [d.id for d in PlacementDrive.query.filter_by(company_id=profile.id).all()]
        if drive_ids:
            # Get all applications for those drives
            apps = StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids)).all()
            
    return render_template("company/applications.html", applications=apps, company_name=company_name)

@company_bp.route("/shortlisted")
@active_account_required
def shortlisted_students():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    company_name = profile.name if profile else "Company User"
    
    shortlisted = []
    if profile:
        drive_ids = [d.id for d in PlacementDrive.query.filter_by(company_id=profile.id).all()]
        if drive_ids:
            shortlisted = StudentApplication.query.filter(
                StudentApplication.drive_id.in_(drive_ids),
                StudentApplication.status == "Shortlisted"
            ).all()
            
    return render_template("company/shortlisted.html", students=shortlisted, company_name=company_name)

@company_bp.route("/selected")
@active_account_required
def selected_students():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    company_name = profile.name if profile else "Company User"
    
    selected = []
    if profile:
        drive_ids = [d.id for d in PlacementDrive.query.filter_by(company_id=profile.id).all()]
        if drive_ids:
            selected = StudentApplication.query.filter(
                StudentApplication.drive_id.in_(drive_ids),
                StudentApplication.status == "Selected"
            ).all()
            
    return render_template("company/selected.html", students=selected, company_name=company_name)

@company_bp.route("/profile")
@active_account_required
def profile():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    
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
    # Note: We'll need to create company/profile.html
    return render_template("company/profile.html", company_name=company_name, company=company_data)
