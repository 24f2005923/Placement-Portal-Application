from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Account, StudentProfile, CompanyProfile, AccountRole, AccountState
from datetime import datetime

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
        institutional_email = request.form.get("college_email")
        password = request.form.get("password")
        
        full_name = request.form.get("full_name")
        university_reg_no = request.form.get("roll_number")
        gender_code = request.form.get("gender")
        dob_str = request.form.get("dob")
        personal_email = request.form.get("personal_email")
        primary_phone = request.form.get("mobile")
        secondary_phone = request.form.get("alt_mobile")

        if Account.query.filter_by(login_identifier=institutional_email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.student_register"))
        
        if StudentProfile.query.filter_by(university_register_number=university_reg_no).first():
            flash("University register number already registered.", "danger")
            return redirect(url_for("auth.student_register"))

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

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
        company_name  = request.form.get("company_name")
        registration_id = request.form.get("company_id_field")
        website       = request.form.get("website")
        industry_type = request.form.get("industry_type")
        location      = request.form.get("location")
        hr_contact    = request.form.get("hr_contact")
        work_email    = request.form.get("work_email")
        password      = request.form.get("password")

        if Account.query.filter_by(login_identifier=work_email).first():
            flash("An account with this email already exists.", "danger")
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
