from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from database import init_db, get_db_connection
from models import Student, Company, Drive, Application, get_counts

app = Flask(__name__)
app.secret_key = "placement_secret_key"

# Initialize Database
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username == "admin@admin" and password == "password":
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid Credentials", "danger")
            return redirect(url_for("admin_login"))
            
    return render_template("admin_login.html")

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = get_db_connection()
        student = conn.execute("SELECT * FROM students WHERE college_email = ? AND password = ?", (email, password)).fetchone()
        conn.close()
        
        if student:
            session["role"] = "student"
            session["student_id"] = student["id"]
            session["student_name"] = student["name"]
            session["student_email"] = student["college_email"]
            flash(f"Welcome back, {student['name']}!", "success")
            return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid Email or Password", "danger")
            return redirect(url_for("student_login"))
    return render_template("student_login.html")

@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        # Placeholder for student registration logic
        flash("Student registration successful!", "success")
        return redirect(url_for("student_login"))
    return render_template("student_register.html")

# Student Panel Routes
@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") == "student":
        return render_template("student_dashboard.html")
    return redirect(url_for("student_login"))

@app.route("/student/profile")
def student_view_profile():
    if session.get("role") == "student":
        return render_template("student_view_profile.html")
    return redirect(url_for("student_login"))

@app.route("/student/profile/edit")
def student_edit_profile():
    if session.get("role") == "student":
        return render_template("student_edit_profile.html")
    return redirect(url_for("student_login"))

@app.route("/student/drives")
def student_view_drives():
    if session.get("role") == "student":
        return render_template("student_view_drives.html")
    return redirect(url_for("student_login"))

@app.route("/student/search")
def student_search_jobs():
    if session.get("role") == "student":
        return render_template("student_view_drives.html") # Reuse drive view for simplicity
    return redirect(url_for("student_login"))

@app.route("/student/applications")
def student_applications():
    if session.get("role") == "student":
        return render_template("student_applications.html")
    return redirect(url_for("student_login"))

@app.route("/student/history")
def student_history():
    if session.get("role") == "student":
        return render_template("student_history.html")
    return redirect(url_for("student_login"))

@app.route("/student/notifications")
def student_notifications():
    if session.get("role") == "student":
        return render_template("student_notifications.html")
    return redirect(url_for("student_login"))

@app.route("/student/settings")
def student_settings():
    if session.get("role") == "student":
        return render_template("student_settings.html")
    return redirect(url_for("student_login"))

@app.route("/student/logout")
def student_logout():
    session.clear()
    flash("Successfully logged out from student portal", "success")
    return redirect(url_for("student_login"))

@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = get_db_connection()
        company = conn.execute("SELECT * FROM companies WHERE work_email = ? AND password = ?", (email, password)).fetchone()
        conn.close()
        
        if company:
            session["role"] = "company"
            session["company_id"] = company["id"]
            session["company_name"] = company["name"]
            flash(f"Logged in successfully as {company['name']}", "success")
            return redirect(url_for("company_dashboard"))
        else:
            flash("Invalid Email or Password", "danger")
            return redirect(url_for("company_login"))
            
    return render_template("company_login.html")

@app.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        # Placeholder for company registration logic
        flash("Company registration submitted for approval!", "success")
        return redirect(url_for("company_login"))
    return render_template("company_register.html")

# Company Panel Routes
@app.route("/company/dashboard")
def company_dashboard():
    return render_template("company_dashboard.html")

@app.route("/company/profile")
def company_profile():
    return render_template("company_profile.html")

@app.route("/company/create-drive")
def company_create_drive():
    return render_template("company_create_drive.html")

@app.route("/company/applications")
def company_applications():
    return render_template("company_applications.html")

@app.route("/company/shortlisted")
def company_shortlisted():
    return render_template("company_shortlisted.html")

@app.route("/company/selected")
def company_selected():
    return render_template("company_selected.html")

@app.route("/company/logout")
def company_logout():
    session.pop("role", None)
    flash("Successfully logged out from company portal", "success")
    return redirect(url_for("company_login"))

@app.route("/admin/dashboard")
def admin_dashboard():
    if "role" in session and session["role"] == "admin":
        counts = get_counts()
        return render_template("admin_dashboard.html", counts=counts)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/students")
def admin_students():
    if "role" in session and session["role"] == "admin":
        students = Student.get_all()
        return render_template("admin_students.html", students=students)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/companies")
def admin_companies():
    if "role" in session and session["role"] == "admin":
        companies = Company.get_all()
        return render_template("admin_companies.html", companies=companies)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/drives")
def admin_drives():
    if "role" in session and session["role"] == "admin":
        drives = Drive.get_all()
        return render_template("admin_drives.html", drives=drives)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/applications")
def admin_applications():
    if "role" in session and session["role"] == "admin":
        applications = Application.get_all()
        return render_template("admin_applications.html", applications=applications)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/blacklisted")
def admin_blacklisted():
    if "role" in session and session["role"] == "admin":
        students = Student.get_blacklisted()
        return render_template("admin_blacklisted.html", students=students)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("role", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
