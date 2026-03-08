from database import db
from models.enums import ApplicationStatus

class StudentApplication(db.Model):
    __tablename__ = "student_applications"
    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive_application'),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    
    status = db.Column(
        db.Enum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.APPLIED
    )
    applied_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=db.func.now())
    
    student = db.relationship("StudentProfile", backref=db.backref("student_applications", lazy=True))
    drive = db.relationship("PlacementDrive", backref=db.backref("job_applications", lazy=True))

    def __repr__(self):
        return f"<StudentApplication {self.student_id} -> {self.drive_id}>"
