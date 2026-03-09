from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database import db
from models import Account, StudentProfile, CompanyProfile, AccountRole, AccountState
from datetime import datetime
import re
import os
from flask import current_app
from werkzeug.utils import secure_filename
from utils.workflow_utils import secure_password_value, store_registration_entry, finalize_workflow

auth_bp = Blueprint("auth", __name__)



def _execute_portal_entry(role_enum, redirect_endpoint):
    """
    Validates user credentials and prepares the session for the specific role.
    """
    identifier = request.form.get("email", "").strip()
    password   = request.form.get("password", "")

    account = Account.query.filter_by(
        login_identifier=identifier, role=role_enum.value
    ).first()

    if account and check_password_hash(account.password_hash, password):
        account.record_login()
        finalize_workflow()
        session["account_id"] = account.id
        session["role"] = account.role.value if hasattr(account.role, 'value') else account.role
        return redirect(url_for(redirect_endpoint))

    return None



@auth_bp.route("/student/register", methods=["GET", "POST"], endpoint="student_register")
def initiate_student_onboarding():
    if request.method == "POST":
        institutional_email = request.form.get("college_email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        full_name = request.form.get("full_name", "").strip()
        university_reg_no = request.form.get("roll_number", "").strip()
        gender_code = request.form.get("gender", "").strip()
        dob_str = request.form.get("dob", "").strip()
        personal_email = request.form.get("personal_email", "").strip()
        primary_phone = request.form.get("mobile", "").strip()
        secondary_phone = request.form.get("alt_mobile", "").strip()

        if not full_name or len(full_name) < 3 or not re.match(r"^[A-Za-z\s]+$", full_name):
            flash("Invalid full name provided.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not university_reg_no or not re.match(r"^[A-Za-z0-9]+$", university_reg_no):
            flash("Register number format is invalid.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not gender_code or gender_code not in ["Male", "Female", "Other"]:
            flash("Please select a valid gender.", "danger")
            return redirect(url_for("auth.student_register"))
            
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if '-' in dob_str and len(dob_str.split('-')[0]) == 4 else datetime.strptime(dob_str, '%d-%m-%Y').date()
        except (ValueError, TypeError):
            flash("Invalid Date of Birth format.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not institutional_email or not institutional_email.endswith("@college.edu"):
            flash("Official email must end with @college.edu.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not personal_email or not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", personal_email):
            flash("Invalid personal email format.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not primary_phone or not re.match(r"^\d{10}$", primary_phone):
            flash("Mobile number must be 10 digits.", "danger")
            return redirect(url_for("auth.student_register"))
                
        if not password or len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            flash("Password requirements not met.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.student_register"))

        if Account.query.filter_by(login_identifier=institutional_email).first():
            flash("Credential already in use.", "danger")
            return redirect(url_for("auth.student_register"))
        
        if StudentProfile.query.filter_by(university_register_number=university_reg_no).first():
            flash("Identity already registered.", "danger")
            return redirect(url_for("auth.student_register"))

        try:
            account = Account(
                login_identifier=institutional_email,
                password_hash=secure_password_value(password),
                role=AccountRole.STUDENT.value,
                account_state=AccountState.PENDING_VERIFICATION.value,
            )
            store_registration_entry(account)

            profile = StudentProfile(
                account_id=account.id,
                full_name=full_name,
                university_register_number=university_reg_no,
                gender_code=gender_code,
                date_of_birth=dob,
                institutional_email=institutional_email,
                personal_email=personal_email,
                primary_phone=primary_phone,
                secondary_phone=secondary_phone
            )
            
            # Handle Resume Upload
            resume_file = request.files.get("resume")
            if resume_file and resume_file.filename:
                allowed_ext = {"pdf", "doc", "docx"}
                ext = resume_file.filename.rsplit(".", 1)[-1].lower()
                if ext in allowed_ext:
                    # Check file size (5MB limit)
                    resume_file.seek(0, os.SEEK_END)
                    file_size = resume_file.tell()
                    resume_file.seek(0)
                    
                    if file_size <= 5 * 1024 * 1024:
                        upload_dir = os.path.join(current_app.root_path, "static", "uploads", "resumes")
                        os.makedirs(upload_dir, exist_ok=True)
                        filename = secure_filename(f"resume_{university_reg_no}.{ext}")
                        resume_file.save(os.path.join(upload_dir, filename))
                        profile.cv_filename = filename
                    else:
                        flash("Resume file size exceeds 5MB limit.", "warning")
                else:
                    flash("Invalid file format for resume. Only PDF/DOC/DOCX allowed.", "warning")
            
            store_registration_entry(profile)
            finalize_workflow()

            flash("Success! Awaiting verification.", "success")
            return redirect(url_for("auth.student_login"))

        except Exception as e:
            db.session.rollback()
            flash(f"System error during onboarding: {str(e)}", "danger")
            return redirect(url_for("auth.student_register"))

    return render_template("auth/student_register.html")



@auth_bp.route("/logout", endpoint="logout")
def terminate_session():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("main.index"))



@auth_bp.route("/admin/login", methods=["GET", "POST"], endpoint="admin_login")
def access_moderation_portal():
    if request.method == "POST":
        result = _execute_portal_entry(AccountRole.ADMIN, "admin.dashboard")
        if result: return result
        flash("Invalid administrative credentials.", "danger")
    return render_template("auth/admin_login.html")


@auth_bp.route("/student/login", methods=["GET", "POST"], endpoint="student_login")
def access_engagement_hub():
    if request.method == "POST":
        result = _execute_portal_entry(AccountRole.STUDENT, "student.dashboard")
        if result: return result
        flash("Invalid student credentials.", "danger")
    return render_template("auth/student_login.html")


@auth_bp.route("/company/login", methods=["GET", "POST"], endpoint="company_login")
def access_organization_panel():
    if request.method == "POST":
        result = _execute_portal_entry(AccountRole.COMPANY, "company.dashboard")
        if result: return result
        flash("Invalid organization credentials.", "danger")
    return render_template("auth/company_login.html")



@auth_bp.route("/company/register", methods=["GET", "POST"], endpoint="company_register")
def register_hiring_partner():
    if request.method == "POST":
        company_name  = request.form.get("company_name", "").strip()
        registration_id = request.form.get("company_id_field", "").strip()
        website       = request.form.get("website", "").strip()
        industry_type = request.form.get("industry_type", "").strip()
        location      = request.form.get("location", "").strip()
        hr_contact    = request.form.get("hr_contact", "").strip()
        work_email    = request.form.get("work_email", "").strip()
        password      = request.form.get("password", "")

        if not company_name or not work_email or not password:
            flash("Required fields are missing.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", work_email):
            flash("Invalid email format.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            flash("Security requirements for password not met.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if not hr_contact or len(hr_contact) < 3 or not re.match(r"^[A-Za-z\s\.\-']+$", hr_contact):
            flash("HR contact details are invalid.", "danger")
            return redirect(url_for("auth.company_register"))

        if Account.query.filter_by(login_identifier=work_email).first() or CompanyProfile.query.filter_by(work_email=work_email).first():
            flash("Organization already exists.", "danger")
            return redirect(url_for("auth.company_register"))
        
        if CompanyProfile.query.filter_by(company_id_field=registration_id).first():
            flash("Registration ID conflict.", "danger")
            return redirect(url_for("auth.company_register"))

        try:
            account = Account(
                login_identifier=work_email,
                password_hash=secure_password_value(password),
                role=AccountRole.COMPANY.value,
                account_state=AccountState.PENDING_VERIFICATION.value,
            )
            store_registration_entry(account)

            profile = CompanyProfile(
                account_id=account.id,
                name=company_name,
                company_id_field=registration_id,
                website_url=website,
                industry_type=industry_type,
                location=location,
                hr_contact=hr_contact,
                work_email=work_email
            )
            store_registration_entry(profile)
            finalize_workflow()

            flash("Partner registration submitted.", "success")
            return redirect(url_for("auth.company_login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error during partner registration: {str(e)}", "danger")
            return redirect(url_for("auth.company_register"))

    return render_template("auth/company_register.html")
