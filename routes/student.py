from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from datetime import datetime
from database import db
from utils.decorators import active_account_required
from models import StudentProfile, PlacementDrive

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
    return render_template("student/dashboard.html", student_name=student_name)

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
            "skills": profile.skills
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
    # Filter: Approved + Deadline hasn't passed
    drives = PlacementDrive.query.filter(
        PlacementDrive.approval_status == 'Approved',
        PlacementDrive.application_deadline >= current_time
    ).order_by(PlacementDrive.application_deadline.asc()).all()
    
    return render_template("student/view_drives.html", drives=drives, student_name=student_name)

@student_bp.route("/applications")
@active_account_required
def applications():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    return render_template("student/applications.html", applications=[], student_name=student_name)

@student_bp.route("/history")
@active_account_required
def history():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    return render_template("student/history.html", student_name=student_name)

@student_bp.route("/notifications")
@active_account_required
def notifications():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    return render_template("student/notifications.html", student_name=student_name)

@student_bp.route("/settings")
@active_account_required
def settings():
    account_id = session.get("account_id")
    profile = StudentProfile.query.filter_by(account_id=account_id).first()
    student_name = profile.full_name if profile else "Student User"
    return render_template("student/settings.html", student_name=student_name)
