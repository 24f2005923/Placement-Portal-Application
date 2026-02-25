from flask import Blueprint, render_template, redirect, url_for, session
from utils.decorators import active_account_required

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.before_request
def student_required():
    if session.get("role") != "student":
        return redirect(url_for("auth.student_login"))

@student_bp.route("/dashboard")
@active_account_required
def dashboard():
    return render_template("student_index.html")

@student_bp.route("/profile")
@active_account_required
def profile():
    return render_template("student_profile.html")

@student_bp.route("/placements")
@active_account_required
def placements():
    return render_template("student_placements.html", drives=[])

@student_bp.route("/applications")
@active_account_required
def applications():
    return render_template("student_applications.html", applications=[])

@student_bp.route("/history")
@active_account_required
def history():
    return render_template("student_history.html")

@student_bp.route("/notifications")
@active_account_required
def notifications():
    return render_template("student_notifications.html")

@student_bp.route("/settings")
@active_account_required
def settings():
    return render_template("student_settings.html")
