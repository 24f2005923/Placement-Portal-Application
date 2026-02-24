from flask import Blueprint, render_template, redirect, url_for, session
from utils.decorators import active_account_required

company_bp = Blueprint("company", __name__, url_prefix="/company")

@company_bp.before_request
def company_required():
    if session.get("role") != "company":
        return redirect(url_for("auth.company_login"))

@company_bp.route("/dashboard")
@active_account_required
def dashboard():
    return render_template("company_index.html")

@company_bp.route("/create-drive")
@active_account_required
def create_drive():
    return render_template("company_create_drive.html")

@company_bp.route("/my-drives")
@active_account_required
def my_drives():
    return render_template("company_my_drives.html", drives=[])

@company_bp.route("/applications")
@active_account_required
def applications():
    return render_template("company_applications.html", applications=[])
