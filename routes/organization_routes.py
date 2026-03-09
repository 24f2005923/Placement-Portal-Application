from flask import Blueprint, render_template, redirect, url_for, session, request, flash, send_from_directory
from utils.decorators import active_account_required
from utils.helpers import get_current_company_profile
from models import CompanyProfile, PlacementDrive, StudentApplication, db, DriveStatus, ApplicationStatus, StudentProfile
import os
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

@company_bp.route("/dashboard", endpoint="dashboard")
@active_account_required
def hiring_partner_overview():
    profile = get_current_company_profile()
    if not profile: return redirect(url_for("auth.company_login"))

    drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
    drive_ids = [d.id for d in drives]
    
    active_count = PlacementDrive.query.filter_by(company_id=profile.id, approval_status=DriveStatus.APPROVED).count()
    total_apps = StudentApplication.query.filter(StudentApplication.drive_id.in_(drive_ids)).count() if drive_ids else 0
    
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
                           recent_drives=recent)

@company_bp.route("/create-drive", methods=["GET", "POST"], endpoint="create_drive")
@active_account_required
def initiate_recruitment_drive():
    profile = get_current_company_profile()
    
    if not profile:
        flash("Company profile not found.", "danger")
        return redirect(url_for("company.dashboard"))

    if request.method == "POST":
        try:
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
    
    approved_count = sum(1 for d in existing_drives if d.approval_status == DriveStatus.APPROVED)
    pending_count = sum(1 for d in existing_drives if d.approval_status == DriveStatus.PENDING)
    
    return render_template("company/create_drive.html", 
                           company_name=company_name, 
                           company_id=profile.company_id_field,
                           drive_id=generated_drive_id,
                            drives=existing_drives,
                           approved_count=approved_count,
                           pending_count=pending_count)

@company_bp.route("/drives/<int:drive_id>/edit", methods=["GET", "POST"], endpoint="edit_drive")
@active_account_required
def edit_recruitment_drive(drive_id):
    profile = get_current_company_profile()
    if not profile:
        return redirect(url_for("auth.company_login"))
    
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    # Security: Ensure company owns the drive
    if drive.company_id != profile.id:
        flash("Unauthorized access to edit this drive.", "danger")
        return redirect(url_for("company.create_drive"))
    
    if request.method == "POST":
        try:
            drive.job_title = request.form.get("job_title")
            drive.job_description = request.form.get("job_description")
            drive.eligibility_criteria = request.form.get("eligibility_criteria")
            drive.job_location = request.form.get("job_location") or "On-Site"
            drive.package_amount = request.form.get("package_amount")
            deadline_str = request.form.get("application_deadline")
            if deadline_str:
                drive.application_deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            
            # Reset approval status to pending after edit if needed (optional)
            # drive.approval_status = DriveStatus.PENDING
            
            db.session.commit()
            flash("Drive details updated successfully.", "success")
            return redirect(url_for("company.create_drive"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating drive: {str(e)}", "danger")
    
    return render_template("company/edit_drive.html", 
                           company_name=profile.name, 
                           drive=drive)

@company_bp.route("/drives/<int:drive_id>/delete", methods=["POST"], endpoint="delete_drive")
@active_account_required
def remove_recruitment_drive(drive_id):
    profile = get_current_company_profile()
    if not profile:
        return redirect(url_for("auth.company_login"))
    
    drive = PlacementDrive.query.get_or_404(drive_id)
    
    # Security checking
    if drive.company_id != profile.id:
        flash("Unauthorized access to delete this drive.", "danger")
        return redirect(url_for("company.create_drive"))
    
    try:
        db.session.delete(drive)
        db.session.commit()
        flash("Placement drive has been removed.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting drive: {str(e)}", "danger")
        
    return redirect(url_for("company.create_drive"))

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
@company_bp.route("/student/<int:student_id>/resume", endpoint="view_resume")
@active_account_required
def view_student_resume(student_id):
    profile = get_current_company_profile()
    if not profile:
        return redirect(url_for("auth.company_login"))
    
    # Security check: Ensure company has access to this student's resume
    # Check if student is shortlisted for any of this company's drives
    drive_ids = [d.id for d in PlacementDrive.query.filter_by(company_id=profile.id).all()]
    if not drive_ids:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("company.dashboard"))
    
    is_shortlisted = StudentApplication.query.filter(
        StudentApplication.student_id == student_id,
        StudentApplication.drive_id.in_(drive_ids),
        StudentApplication.status == ApplicationStatus.SHORTLISTED
    ).first()
    
    if not is_shortlisted:
        flash("You can only view resumes of students shortlisted for your drives.", "warning")
        return redirect(url_for("company.shortlisted_students"))
    
    student = StudentProfile.query.get_or_404(student_id)
    if not student.cv_filename:
        flash("Resume not uploaded by student.", "info")
        return redirect(url_for("company.shortlisted_students"))
    
    # Serve file from static/uploads/resumes
    resume_path = os.path.join("static", "uploads", "resumes")
    return send_from_directory(resume_path, student.cv_filename)
