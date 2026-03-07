from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from database import db
from utils.decorators import active_account_required
from utils.helpers import get_current_student_profile
from models import StudentProfile, PlacementDrive, StudentApplication, Notification, DriveStatus, ApplicationStatus

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.before_request
def student_required():
    # checking if it's actually a student session and not someone trying to bypass
    if session.get("role") != "student":
        return redirect(url_for("auth.student_login"))

@student_bp.route("/dashboard", endpoint="dashboard")
@active_account_required
def engagement_portal_main():
    profile = get_current_student_profile()
    student_name = profile.full_name if profile else "Student User"
    
    latest_drives = []
    app_count = 0
    unread_notifications_count = 0
    recent_notifications = []
    
    if profile:
        current_time = datetime.now()
        # fetch recently approved drives for candidates
        latest_drives = PlacementDrive.query.filter(
            PlacementDrive.approval_status == DriveStatus.APPROVED,
            PlacementDrive.application_deadline >= current_time
        ).order_by(PlacementDrive.created_at.desc()).limit(5).all()
        
        app_count = StudentApplication.query.filter_by(student_id=profile.id).count()
        
        unread_notifications_count = Notification.query.filter_by(
            student_id=profile.id, 
            is_read=False
        ).count()
        
        recent_notifications = Notification.query.filter_by(
            student_id=profile.id
        ).order_by(Notification.created_at.desc()).limit(5).all()
        
        applied_drive_ids = [app.drive_id for app in StudentApplication.query.filter_by(student_id=profile.id).all()]
        
        # quick status calculation for personal metrics
        status_counts = {
            'Applied': StudentApplication.query.filter_by(student_id=profile.id, status=ApplicationStatus.APPLIED).count(),
            'Shortlisted': StudentApplication.query.filter_by(student_id=profile.id, status=ApplicationStatus.SHORTLISTED).count(),
            'Selected': StudentApplication.query.filter_by(student_id=profile.id, status=ApplicationStatus.SELECTED).count(),
            'Rejected': StudentApplication.query.filter_by(student_id=profile.id, status=ApplicationStatus.REJECTED).count()
        }
        
    return render_template(
        "student/dashboard.html", 
        student_name=student_name,
        latest_drives=latest_drives,
        app_count=app_count,
        unread_count=unread_notifications_count,
        recent_notifications=recent_notifications,
        applied_drive_ids=applied_drive_ids,
        status_counts=status_counts if profile else {}
    )

@student_bp.route("/profile", methods=["GET", "POST"], endpoint="profile")
@active_account_required
def manage_candidate_profile():
    profile = get_current_student_profile()
    
    if request.method == "POST":
        if profile:
            # persisting candidate updates
            profile.full_name = request.form.get("name")
            profile.personal_email = request.form.get("personal_email")
            profile.primary_phone = request.form.get("mobile")
            dob_str = request.form.get("dob")
            if dob_str:
                profile.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            profile.skills = request.form.get("skills")
            cv_file = request.files.get("cv")
            if cv_file and cv_file.filename:
                allowed = {"pdf", "doc", "docx"}
                ext = cv_file.filename.rsplit(".", 1)[-1].lower()
                if ext in allowed:
                    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "cvs")
                    os.makedirs(upload_dir, exist_ok=True)
                    filename = secure_filename(f"cv_{profile.id}.{ext}")
                    cv_file.save(os.path.join(upload_dir, filename))
                    profile.cv_filename = filename
                else:
                    flash("Only PDF, DOC, or DOCX files are allowed for CV.", "danger")
                    return redirect(url_for("student.profile"))
            db.session.commit()
            flash("Profile updated successfully!", "success")
        return redirect(url_for("student.profile"))

    student_data = None
    if profile:
        student_data = {
            "name": profile.full_name,
            "roll_number": profile.university_register_number,
            "gender": profile.gender_code,
            "college_email": profile.institutional_email,
            "personal_email": profile.personal_email,
            "mobile": profile.primary_phone,
            "dob": profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else None,
            "skills": profile.skills,
            "cv_filename": profile.cv_filename
        }

    student_name = profile.full_name if profile else "Student User"
    return render_template("student/profile.html", student_name=student_name, student=student_data)

@student_bp.route("/placements", endpoint="placements")
@active_account_required
def search_career_opportunities():
    profile = get_current_student_profile()
    student_name = profile.full_name if profile else "Student User"
    search_query = request.args.get('search', '').strip()
    
    current_time = datetime.now()
    query = PlacementDrive.query.filter(
        PlacementDrive.approval_status == DriveStatus.APPROVED,
        PlacementDrive.application_deadline >= current_time
    )

    if search_query:
        from models import CompanyProfile
        query = query.join(CompanyProfile).filter(
            db.or_(
                PlacementDrive.job_title.ilike(f"%{search_query}%"),
                PlacementDrive.job_location.ilike(f"%{search_query}%"),
                db.cast(PlacementDrive.package_amount, db.String).ilike(f"%{search_query}%"),
                CompanyProfile.name.ilike(f"%{search_query}%")
            )
        )

    drives = query.order_by(PlacementDrive.application_deadline.asc()).all()
    
    applied_drive_ids = []
    if profile:
        applied_drive_ids = [app.drive_id for app in StudentApplication.query.filter_by(student_id=profile.id).all()]
    
    return render_template("student/view_drives.html", drives=drives, student_name=student_name, 
                           applied_drive_ids=applied_drive_ids, search_query=search_query)


@student_bp.route("/applications", endpoint="applications")
@active_account_required
def review_my_submissions():
    profile = get_current_student_profile()
    student_name = profile.full_name if profile else "Student User"
    search_query = request.args.get('search', '').strip()
    
    apps = []
    if profile:
        query = StudentApplication.query.filter_by(student_id=profile.id)
        if search_query:
            from models import PlacementDrive, CompanyProfile
            query = query.join(PlacementDrive).join(CompanyProfile).filter(
                db.or_(
                    PlacementDrive.job_title.ilike(f"%{search_query}%"),
                    CompanyProfile.name.ilike(f"%{search_query}%"),
                    db.cast(StudentApplication.status, db.String).ilike(f"%{search_query}%")
                )
            )
        apps = query.all()
        
    return render_template("student/applications.html", applications=apps, student_name=student_name, search_query=search_query)


@student_bp.route("/history", endpoint="history")
@active_account_required
def view_placement_history():
    profile = get_current_student_profile()
    student_name = profile.full_name if profile else "Student User"
    search_query = request.args.get('search', '').strip()
    
    selected_apps = []
    if profile:
        query = StudentApplication.query.filter_by(
            student_id=profile.id, 
            status=ApplicationStatus.SELECTED
        )
        if search_query:
            from models import PlacementDrive, CompanyProfile
            query = query.join(PlacementDrive).join(CompanyProfile).filter(
                db.or_(
                    PlacementDrive.job_title.ilike(f"%{search_query}%"),
                    CompanyProfile.name.ilike(f"%{search_query}%")
                )
            )
        selected_apps = query.all()
        
    return render_template("student/history.html", student_name=student_name, applications=selected_apps, search_query=search_query)


@student_bp.route("/notifications", endpoint="notifications")
@active_account_required
def check_system_alerts():
    profile = get_current_student_profile()
    student_name = profile.full_name if profile else "Student User"
    search_query = request.args.get('search', '').strip()
    
    notifications_list = []
    if profile:
        query = Notification.query.filter_by(student_id=profile.id)
        if search_query:
            query = query.filter(
                db.or_(
                    Notification.message.ilike(f"%{search_query}%"),
                    db.cast(Notification.category, db.String).ilike(f"%{search_query}%")
                )
            )
        notifications_list = query.order_by(Notification.created_at.desc()).all()

    return render_template("student/notifications.html", student_name=student_name, 
                           notifications=notifications_list, search_query=search_query)
