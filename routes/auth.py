from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import Account, StudentProfile, AccountRole, AccountState
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        institutional_email = request.form.get("college_email")
        password = request.form.get("password")
        
        # Profile fields
        full_name = request.form.get("full_name")
        university_reg_no = request.form.get("roll_number")
        gender_code = request.form.get("gender")
        dob_str = request.form.get("dob")
        personal_email = request.form.get("personal_email")
        primary_phone = request.form.get("mobile")
        secondary_phone = request.form.get("alt_mobile")

        # Basic uniqueness checks
        if Account.query.filter_by(login_identifier=institutional_email).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.student_register"))
        
        if StudentProfile.query.filter_by(university_register_number=university_reg_no).first():
            flash("University register number already registered.", "danger")
            return redirect(url_for("auth.student_register"))

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

            # Create Account
            account = Account(
                login_identifier=institutional_email,
                password_hash=generate_password_hash(password),
                role=AccountRole.STUDENT,
                account_state=AccountState.PENDING_VERIFICATION,
            )
            db.session.add(account)
            db.session.flush() # Get the account ID

            # Create StudentProfile
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
            return redirect(url_for("auth.login"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error during registration: {str(e)}", "danger")
            return redirect(url_for("auth.student_register"))

    return render_template("student_register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("email")
        password = request.form.get("password")
        
        account = Account.query.filter_by(login_identifier=identifier).first()
        
        if account and check_password_hash(account.password_hash, password):
            account.record_login()
            db.session.commit()
            
            session["account_id"] = account.id
            session["role"] = account.role.value
            
            if account.role == AccountRole.ADMIN:
                return redirect(url_for("admin.dashboard"))
            elif account.role == AccountRole.STUDENT:
                return redirect(url_for("student.dashboard"))
            elif account.role == AccountRole.COMPANY:
                return redirect(url_for("company.dashboard"))
        
        flash("Invalid credentials or account suspended.", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))

@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        identifier = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        print(f"DEBUG: Admin login attempt with identifier: '{identifier}'")
        
        account = Account.query.filter_by(login_identifier=identifier, role=AccountRole.ADMIN).first()
        
        if account:
            print(f"DEBUG: Found account: {account}")
            is_match = check_password_hash(account.password_hash, password)
            print(f"DEBUG: Password match: {is_match}")
            
            if is_match:
                account.record_login()
                db.session.commit()
                session["account_id"] = account.id
                session["role"] = account.role.value
                return redirect(url_for("admin.dashboard"))
        else:
            print(f"DEBUG: No admin account found with identifier: '{identifier}'")
        
        flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")

@auth_bp.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        identifier = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        account = Account.query.filter_by(login_identifier=identifier, role=AccountRole.STUDENT).first()
        
        if account and check_password_hash(account.password_hash, password):
            account.record_login()
            db.session.commit()
            session["account_id"] = account.id
            session["role"] = account.role.value
            return redirect(url_for("student.dashboard"))
        
        flash("Invalid student credentials.", "danger")
    return render_template("student_login.html")

@auth_bp.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        identifier = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        account = Account.query.filter_by(login_identifier=identifier, role=AccountRole.COMPANY).first()
        
        if account and check_password_hash(account.password_hash, password):
            account.record_login()
            db.session.commit()
            session["account_id"] = account.id
            session["role"] = account.role.value
            return redirect(url_for("company.dashboard"))
        
        flash("Invalid company credentials.", "danger")
    return render_template("company_login.html")
