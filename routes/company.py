from flask import Blueprint, render_template, redirect, url_for, session, request
from utils.decorators import active_account_required
from models import CompanyProfile

company_bp = Blueprint("company", __name__, url_prefix="/company")

@company_bp.before_request
def company_required():
    if session.get("role") != "company":
        return redirect(url_for("auth.company_login"))

@company_bp.route("/dashboard")
@active_account_required
def dashboard():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    company_name = profile.name if profile else "Company User"
    return render_template("company/dashboard.html", company_name=company_name)

@company_bp.route("/create-drive")
@active_account_required
def create_drive():
    account_id = session.get("account_id")
    profile = CompanyProfile.query.filter_by(account_id=account_id).first()
    company_name = profile.name if profile else "Company User"
    return render_template("company/create_drive.html", company_name=company_name)

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
    return render_template("company/applications.html", applications=[], company_name=company_name)

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
