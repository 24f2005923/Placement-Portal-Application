from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from database import db
from utils.decorators import active_account_required
from models import StudentProfile, PlacementDrive, StudentApplication, Notification

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.before_request
def student_required():
    if session.get("role") != "student":
        return redirect(url_for("auth.student_login"))

@student_bp.route("/dashboard")
@active_account_required
def dashboard():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    
    latest_drives = []
    app_count = 0
    unread_notifications_count = 0
    recent_notifications = []
    
    if profile:
        current_time = datetime.now()
        latest_drives = PlacementDrive.query.filter(
            PlacementDrive.approval_status == 'Approved',
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
        
    return render_template(
        "student/dashboard.html", 
        student_name=student_name,
        latest_drives=latest_drives,
        app_count=app_count,
        unread_count=unread_notifications_count,
        recent_notifications=recent_notifications,
        applied_drive_ids=applied_drive_ids
    )

@student_bp.route("/profile", methods=["GET", "POST"])
@active_account_required
def profile():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    
    if request.method == "POST":
        if profile:
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

@student_bp.route("/placements")
@active_account_required
def placements():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    
    current_time = datetime.now()
    drives = PlacementDrive.query.filter(
        PlacementDrive.approval_status == 'Approved',
        PlacementDrive.application_deadline >= current_time
    ).order_by(PlacementDrive.application_deadline.asc()).all()
    
    applied_drive_ids = []
    if profile:
        applied_drive_ids = [app.drive_id for app in StudentApplication.query.filter_by(student_id=profile.id).all()]
    
    return render_template("student/view_drives.html", drives=drives, student_name=student_name, applied_drive_ids=applied_drive_ids)

@student_bp.route("/applications")
@active_account_required
def applications():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    
    apps = []
    if profile:
        apps = StudentApplication.query.filter_by(student_id=profile.id).all()
        
    return render_template("student/applications.html", applications=apps, student_name=student_name)

@student_bp.route("/history")
@active_account_required
def history():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    
    selected_apps = []
    if profile:
        selected_apps = StudentApplication.query.filter_by(
            student_id=profile.id, 
            status='Selected'
        ).all()
        
    return render_template("student/history.html", student_name=student_name, applications=selected_apps)

@student_bp.route("/notifications")
@active_account_required
def notifications():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    return render_template("student/notifications.html", student_name=student_name)
