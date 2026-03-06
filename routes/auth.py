from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Account, StudentProfile, CompanyProfile, AccountRole, AccountState
from datetime import datetime
import re

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------------------------
# Private helper — shared authentication logic for all three portals
# ---------------------------------------------------------------------------

def _handle_login(role_enum, redirect_endpoint):
    """
    Reads email/password from the current POST request, looks up the matching
    Account by login_identifier + role, validates the password, sets the
    session, and returns a redirect Response on success or None on failure.
    """
    identifier = request.form.get("email", "").strip()
    password   = request.form.get("password", "")

    account = Account.query.filter_by(
        login_identifier=identifier, role=role_enum
    ).first()

    if account and check_password_hash(account.password_hash, password):
        account.record_login()
        db.session.commit()
        session["account_id"] = account.id
        session["role"]       = account.role.value
        return redirect(url_for(redirect_endpoint))

    return None   # caller is responsible for flashing an error


# ---------------------------------------------------------------------------
# Student registration
# ---------------------------------------------------------------------------

@auth_bp.route("/student/register", methods=["GET", "POST"])
def student_register():
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

        if not full_name:
            flash("Full name must not be empty.", "danger")
            return redirect(url_for("auth.student_register"))
        if len(full_name) < 3 or not re.match(r"^[A-Za-z\s]+$", full_name):
            flash("Full name must be at least 3 characters and contain only alphabets and spaces.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not university_reg_no or not re.match(r"^[A-Za-z0-9]+$", university_reg_no):
            flash("Register number must not be empty and must follow alphanumeric format like 2023CS101.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not gender_code or gender_code not in ["Male", "Female", "Other"]:
            flash("Please select a valid gender.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not dob_str:
            flash("Date of Birth is required.", "danger")
            return redirect(url_for("auth.student_register"))
            
        try:
            if '-' in dob_str and len(dob_str.split('-')[0]) == 4:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            else:
                dob = datetime.strptime(dob_str, '%d-%m-%Y').date()
        except ValueError:
            flash("Date of Birth must be a valid date in format dd-mm-yyyy.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not institutional_email:
            flash("Official College Email must not be empty.", "danger")
            return redirect(url_for("auth.student_register"))
        if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", institutional_email) or not institutional_email.endswith("@college.edu"):
            flash("Official College Email must be valid and end with @college.edu.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not personal_email or not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", personal_email):
            flash("Personal Email must be a valid email format.", "danger")
            return redirect(url_for("auth.student_register"))
        if personal_email == institutional_email:
            flash("Personal Email should not be the same as Official College Email.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if not primary_phone or not re.match(r"^\d{10}$", primary_phone):
            flash("Mobile Number must contain exactly 10 digits.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if secondary_phone:
            if not re.match(r"^\d{10}$", secondary_phone):
                flash("Alternate Mobile Number must contain exactly 10 digits.", "danger")
                return redirect(url_for("auth.student_register"))
            if secondary_phone == primary_phone:
                flash("Alternate Mobile Number should not be the same as Mobile Number.", "danger")
                return redirect(url_for("auth.student_register"))
                
        if not password or len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            flash("Password must be at least 8 characters long and contain both letters and numbers.", "danger")
            return redirect(url_for("auth.student_register"))
            
        if password != confirm_password:
            flash("Password and Confirm Password must match.", "danger")
            return redirect(url_for("auth.student_register"))

        if Account.query.filter_by(login_identifier=institutional_email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.student_register"))
        
        if StudentProfile.query.filter_by(university_register_number=university_reg_no).first():
            flash("University register number already registered.", "danger")
            return redirect(url_for("auth.student_register"))

        try:

            account = Account(
                login_identifier=institutional_email,
                password_hash=generate_password_hash(password),
                role=AccountRole.STUDENT,
                account_state=AccountState.PENDING_VERIFICATION,
            )
            db.session.add(account)
            db.session.flush() # Get the account ID

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
            db.session.add(profile)
            db.session.commit()

            flash("Registration successful! Await admin verification.", "success")
            return redirect(url_for("auth.student_login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {str(e)}", "danger")
            return redirect(url_for("auth.student_register"))

    return render_template("auth/student_register.html")


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# Login routes — each delegates to _handle_login()
# ---------------------------------------------------------------------------

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        result = _handle_login(AccountRole.ADMIN, "admin.dashboard")
        if result:
            return result
        flash("Invalid admin credentials.", "danger")
    return render_template("auth/admin_login.html")


@auth_bp.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        result = _handle_login(AccountRole.STUDENT, "student.dashboard")
        if result:
            return result
        flash("Invalid student credentials.", "danger")
    return render_template("auth/student_login.html")


@auth_bp.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        result = _handle_login(AccountRole.COMPANY, "company.dashboard")
        if result:
            return result
        flash("Invalid company credentials.", "danger")
    return render_template("auth/company_login.html")


# ---------------------------------------------------------------------------
# Company registration
# ---------------------------------------------------------------------------

@auth_bp.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        company_name  = request.form.get("company_name", "").strip()
        registration_id = request.form.get("company_id_field", "").strip()
        website       = request.form.get("website", "").strip()
        industry_type = request.form.get("industry_type", "").strip()
        location      = request.form.get("location", "").strip()
        hr_contact    = request.form.get("contact_number") or request.form.get("hr_contact", "").strip()
        work_email    = request.form.get("work_email", "").strip()
        password      = request.form.get("password", "")

        if not company_name:
            flash("Company name must not be empty.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if not work_email:
            flash("Email must not be empty.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if not re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", work_email):
            flash("Invalid email format.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if not password:
            flash("Password must not be empty.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            flash("Password must be at least 8 characters long and contain at least one letter and one number.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if not hr_contact:
            flash("Contact number must not be empty.", "danger")
            return redirect(url_for("auth.company_register"))
            
        if not re.match(r"^\d{10,12}$", hr_contact):
            flash("Contact number must contain only digits and be between 10 and 12 characters.", "danger")
            return redirect(url_for("auth.company_register"))

        if Account.query.filter_by(login_identifier=work_email).first() or CompanyProfile.query.filter_by(work_email=work_email).first():
            flash("Company with this email already exists", "danger")
            return redirect(url_for("auth.company_register"))
        
        if CompanyProfile.query.filter_by(company_id_field=registration_id).first():
            flash("Company ID already registered.", "danger")
            return redirect(url_for("auth.company_register"))

        try:
            account = Account(
                login_identifier=work_email,
                password_hash=generate_password_hash(password),
                role=AccountRole.COMPANY,
                account_state=AccountState.PENDING_VERIFICATION,
            )
            db.session.add(account)
            db.session.flush()

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
            db.session.add(profile)
            db.session.commit()

            flash("Registration successful! Await admin verification.", "success")
            return redirect(url_for("auth.company_login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {str(e)}", "danger")
            return redirect(url_for("auth.company_register"))

    return render_template("auth/company_register.html")
