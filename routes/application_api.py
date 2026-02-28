from flask import Blueprint, jsonify, session
from models import StudentProfile, PlacementDrive, StudentApplication, CompanyProfile, db
from datetime import datetime

application_api_bp = Blueprint("application_api", __name__)

@application_api_bp.route("/api/apply/<int:drive_id>", methods=["POST"])
def apply_to_drive(drive_id):
    # 1. Check if student is logged in
    if session.get("role") != "student" or not session.get("account_id"):
        return jsonify({"message": "Unauthorized"}), 401

    account_id = session.get("account_id")
    student = StudentProfile.query.filter_by(account_id=account_id).first()

    if not student:
        return jsonify({"message": "Student profile not found"}), 404

    # 2. Check if drive exists
    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    # 3. Check if student has already applied
    existing_application = StudentApplication.query.filter_by(
        student_id=student.id, drive_id=drive_id
    ).first()
    
    if existing_application:
        return jsonify({"message": "Already applied"}), 400

    # 4. Create new Application
    try:
        new_app = StudentApplication(
            student_id=student.id,
            drive_id=drive_id,
            status="Applied",
            applied_at=datetime.now()
        )
        db.session.add(new_app)
        db.session.commit()
        return jsonify({"message": "Application submitted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@application_api_bp.route("/api/applications", methods=["GET"])
def get_all_applications():
    # Requirement: For Admin view
    if session.get("role") != "admin":
        return jsonify({"message": "Unauthorized"}), 401

    applications = StudentApplication.query.all()
    results = []
    
    for app in applications:
        results.append({
            "id": app.id,
            "student_name": app.student.full_name,
            "roll_number": app.student.university_register_number,
            "drive_title": app.drive.job_title,
            "company_name": app.drive.company.name,
            "status": app.status,
            "applied_at": app.applied_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(results), 200

@application_api_bp.route("/api/company/applications", methods=["GET"])
def get_company_applications():
    # Requirement: For Company view
    if session.get("role") != "company" or not session.get("account_id"):
        return jsonify({"message": "Unauthorized"}), 401

    account_id = session.get("account_id")
    company_profile = CompanyProfile.query.filter_by(account_id=account_id).first()

    if not company_profile:
        return jsonify({"message": "Company profile not found"}), 404

    # Filter applications where drive.company_id == company_profile.id
    applications = StudentApplication.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company_profile.id
    ).all()

    results = []
    for app in applications:
        results.append({
            "id": app.id,
            "student_name": app.student.full_name,
            "roll_number": app.student.university_register_number,
            "drive_title": app.drive.job_title,
            "status": app.status,
            "applied_at": app.applied_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify(results), 200
