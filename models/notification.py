from database import db
from models.enums import NotificationType

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    category = db.Column(
        db.Enum(NotificationType),
        nullable=False,
        default=NotificationType.INFO
    ) # e.g., Success, Warning, Info
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    student = db.relationship("StudentProfile", backref=db.backref("notifications", lazy=True))

    def __repr__(self):
        return f"<Notification {self.id} for Student {self.student_id}>"
