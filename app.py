from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import configure_db, db
from models import Account, AccountRole, AccountState

app = Flask(__name__)
app.secret_key = "placement_secret_key"

configure_db(app)

with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Landing
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        identifier = request.form["username"]
        password   = request.form["password"]

        account = Account.query.filter_by(
            login_identifier=identifier,
            role=AccountRole.ADMIN,
        ).first()

        if account and check_password_hash(account.password_hash, password):
            if not account.is_active():
                flash("This admin account is not active.", "warning")
                return redirect(url_for("admin_login"))

            account.record_login()
            db.session.commit()

            session["role"]       = "admin"
            session["account_id"] = account.id
            return redirect(url_for("admin_dashboard"))

        flash("Invalid credentials.", "danger")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html", counts={
        "students": 0, "companies": 0, "drives": 0, "applications": 0
    })


@app.route("/admin/students")
def admin_students():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    return render_template("admin_students.html", students=[])


@app.route("/admin/companies")
def admin_companies():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    return render_template("admin_companies.html", companies=[])


@app.route("/admin/drives")
def admin_drives():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    return render_template("admin_drives.html", drives=[])


@app.route("/admin/applications")
def admin_applications():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    return render_template("admin_applications.html", applications=[])


@app.route("/admin/blacklisted")
def admin_blacklisted():
    if session.get("role") != "admin":
        return redirect(url_for("admin_login"))
    return render_template("admin_blacklisted.html", students=[])


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        identifier = request.form["email"]
        password   = request.form["password"]

        account = Account.query.filter_by(
            login_identifier=identifier,
            role=AccountRole.STUDENT,
        ).first()

        if account and check_password_hash(account.password_hash, password):
            if not account.is_active():
                flash("Your account is pending verification or has been suspended.", "warning")
                return redirect(url_for("student_login"))

            account.record_login()
            db.session.commit()

            session["role"]       = "student"
            session["account_id"] = account.id
            flash("Logged in successfully.", "success")
            return redirect(url_for("student_dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("student_login"))

    return render_template("student_login.html")


@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        identifier = request.form.get("college_email")
        password   = request.form.get("password")

        if Account.query.filter_by(login_identifier=identifier).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("student_register"))

        account = Account(
            login_identifier=identifier,
            password_hash=generate_password_hash(password),
            role=AccountRole.STUDENT,
            account_state=AccountState.PENDING_VERIFICATION,
        )
        db.session.add(account)
        db.session.commit()

        flash("Registration submitted. Await admin verification.", "success")
        return redirect(url_for("student_login"))

    return render_template("student_register.html")


@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_dashboard.html",
                           app_count=0, latest_drives=[], recent_apps=[])


@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_profile.html", student=None)


@app.route("/student/drives")
def student_view_drives():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_view_drives.html", drives=[])


@app.route("/student/search")
def student_search_jobs():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_view_drives.html", drives=[])


@app.route("/student/applications")
def student_applications():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_applications.html", applications=[])


@app.route("/student/history")
def student_history():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_history.html")


@app.route("/student/notifications")
def student_notifications():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_notifications.html")


@app.route("/student/settings")
def student_settings():
    if session.get("role") != "student":
        return redirect(url_for("student_login"))
    return render_template("student_settings.html")


@app.route("/student/logout")
def student_logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("student_login"))


# ---------------------------------------------------------------------------
# Company
# ---------------------------------------------------------------------------

@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        identifier = request.form["email"]
        password   = request.form["password"]

        account = Account.query.filter_by(
            login_identifier=identifier,
            role=AccountRole.COMPANY,
        ).first()

        if account and check_password_hash(account.password_hash, password):
            if not account.is_active():
                flash("Your company account is pending approval.", "warning")
                return redirect(url_for("company_login"))

            account.record_login()
            db.session.commit()

            session["role"]       = "company"
            session["account_id"] = account.id
            flash("Logged in successfully.", "success")
            return redirect(url_for("company_dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("company_login"))

    return render_template("company_login.html")


@app.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        identifier = request.form.get("work_email")
        password   = request.form.get("password")

        if Account.query.filter_by(login_identifier=identifier).first():
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("company_register"))

        account = Account(
            login_identifier=identifier,
            password_hash=generate_password_hash(password),
            role=AccountRole.COMPANY,
            account_state=AccountState.PENDING_VERIFICATION,
        )
        db.session.add(account)
        db.session.commit()

        flash("Registration submitted for admin approval.", "success")
        return redirect(url_for("company_login"))

    return render_template("company_register.html")


@app.route("/company/dashboard")
def company_dashboard():
    if session.get("role") != "company":
        return redirect(url_for("company_login"))
    return render_template("company_dashboard.html",
                           active_drives=0, total_apps=0,
                           pending_review=0, hired=0, recent_drives=[])


@app.route("/company/profile")
def company_profile():
    if session.get("role") != "company":
        return redirect(url_for("company_login"))
    return render_template("company_profile.html")


@app.route("/company/create-drive")
def company_create_drive():
    if session.get("role") != "company":
        return redirect(url_for("company_login"))
    return render_template("company_create_drive.html")


@app.route("/company/applications")
def company_applications():
    if session.get("role") != "company":
        return redirect(url_for("company_login"))
    return render_template("company_applications.html", applications=[])


@app.route("/company/shortlisted")
def company_shortlisted():
    if session.get("role") != "company":
        return redirect(url_for("company_login"))
    return render_template("company_shortlisted.html", students=[])


@app.route("/company/selected")
def company_selected():
    if session.get("role") != "company":
        return redirect(url_for("company_login"))
    return render_template("company_selected.html", students=[])


@app.route("/company/logout")
def company_logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("company_login"))


if __name__ == "__main__":
    app.run(debug=True)
