from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "placement_secret_key"

@app.route("/")
def home():
    return "Placement Portal Running Successfully!"

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

@app.route("/admin/dashboard")
def admin_dashboard():
    if "role" in session and session["role"] == "admin":
        return render_template("admin_dashboard.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/students")
def admin_students():
    if "role" in session and session["role"] == "admin":
        return render_template("admin_students.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/companies")
def admin_companies():
    if "role" in session and session["role"] == "admin":
        return render_template("admin_companies.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/drives")
def admin_drives():
    if "role" in session and session["role"] == "admin":
        return render_template("admin_drives.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/applications")
def admin_applications():
    if "role" in session and session["role"] == "admin":
        return render_template("admin_applications.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/blacklisted")
def admin_blacklisted():
    if "role" in session and session["role"] == "admin":
        return render_template("admin_blacklisted.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("role", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
