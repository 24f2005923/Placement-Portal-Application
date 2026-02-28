from datetime import datetime
from database import db

# Clean, student-level model for tracking applications
class StudentApplication(db.Model):
    __tablename__ = "student_applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    
    # Default status set as "Applied" as per requirements
    status = db.Column(db.String(50), default="Applied")
    applied_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True) # For future stage updates
    
    # Meaningful relationships for easy traversal
    student = db.relationship("StudentProfile", backref=db.backref("student_applications", lazy=True))
    drive = db.relationship("PlacementDrive", backref=db.backref("job_applications", lazy=True))

    def __repr__(self):
        return f"<StudentApplication {self.student_id} -> {self.drive_id}>"
