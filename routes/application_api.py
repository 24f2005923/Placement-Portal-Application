from flask import Blueprint, session, jsonify, request
from models import StudentProfile, PlacementDrive, StudentApplication, CompanyProfile, Notification, db, ApplicationStatus, NotificationType
from sqlalchemy.exc import IntegrityError

application_api_bp = Blueprint("application_api", __name__)

@application_api_bp.route("/api/apply/<int:drive_id>", methods=["POST"])
def apply_to_drive(drive_id):
    if session.get("role") != "student" or not session.get("account_id"):
        return jsonify({"message": "Unauthorized"}), 401

    account_id = session.get("account_id")
    student = StudentProfile.query.filter_by(account_id=account_id).first()

    if not student:
        return jsonify({"message": "Student profile not found"}), 404

    drive = PlacementDrive.query.get(drive_id)
    if not drive:
        return jsonify({"message": "Drive not found"}), 404

    # We still check for existing application for a better error message
    existing_application = StudentApplication.query.filter_by(
        student_id=student.id, drive_id=drive_id
    ).first()
    
    if existing_application:
        return jsonify({"message": "Already applied"}), 400

    try:
        new_app = StudentApplication(
            student_id=student.id,
            drive_id=drive_id,
            status=ApplicationStatus.APPLIED
        )
        db.session.add(new_app)
        db.session.commit()
        return jsonify({"message": "Application submitted successfully"}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Already applied (database constraint)"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@application_api_bp.route("/api/applications", methods=["GET"])
def get_all_applications():
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
    if session.get("role") != "company" or not session.get("account_id"):
        return jsonify({"message": "Unauthorized"}), 401

    account_id = session.get("account_id")
    company_profile = CompanyProfile.query.filter_by(account_id=account_id).first()

    if not company_profile:
        return jsonify({"message": "Company profile not found"}), 404

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

@application_api_bp.route("/api/applications/<int:app_id>/update-status", methods=["POST"])
def update_application_status(app_id):
    role = session.get("role")
    if role not in ["admin", "company"]:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    new_status = data.get("status") # e.g., "Shortlisted", "Selected", "Rejected"

    if not new_status:
        return jsonify({"message": "Status is required"}), 400

    app = StudentApplication.query.get(app_id)
    if not app:
        return jsonify({"message": "Application not found"}), 404

    if role == "company":
        account_id = session.get("account_id")
        company = CompanyProfile.query.filter_by(account_id=account_id).first()
        if not company or app.drive.company_id != company.id:
            return jsonify({"message": "Unauthorized"}), 401

    msg = f"Your application for {app.drive.job_title} at {app.drive.company.name} has been updated to '{new_status}'."
    
    # Map string status to Enum if possible, or use logic for category
    try:
        enum_status = ApplicationStatus[new_status.upper()]
        app.status = enum_status
    except (KeyError, AttributeError):
        # Fallback if status name doesn't match enum exactly
        pass

    category = NotificationType.SUCCESS if new_status == "Selected" else (NotificationType.WARNING if new_status == "Rejected" else NotificationType.INFO)
    
    try:
        notification = Notification(
            student_id=app.student_id,
            message=msg,
            category=category
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({"message": "Status updated and student notified"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error: {str(e)}"}), 500

@application_api_bp.route("/api/notifications", methods=["GET"])
def get_student_notifications():
    if session.get("role") != "student":
        return jsonify({"message": "Unauthorized"}), 401
    
    account_id = session.get("account_id")
    student = StudentProfile.query.filter_by(account_id=account_id).first()
    
    if not student:
        return jsonify({"message": "Student not found"}), 404
        
    notifications = Notification.query.filter_by(student_id=student.id).order_by(Notification.created_at.desc()).all()
    results = []
    for n in notifications:
        results.append({
            "id": n.id,
            "message": n.message,
            "category": n.category,
            "is_read": n.is_read,
            "created_at": n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(results), 200

@application_api_bp.route("/api/notifications/mark-read", methods=["POST"])
def mark_notifications_read():
    if session.get("role") != "student":
        return jsonify({"message": "Unauthorized"}), 401
    
    account_id = session.get("account_id")
    student = StudentProfile.query.filter_by(account_id=account_id).first()
    
    if student:
        Notification.query.filter_by(student_id=student.id, is_read=False).update({"is_read": True})
        db.session.commit()
        
    return jsonify({"message": "Marked all as read"}), 200
