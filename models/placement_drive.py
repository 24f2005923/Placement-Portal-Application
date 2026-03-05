from datetime import datetime, timezone
from sqlalchemy import Enum as SAEnum
from database import db
from models.enums import DriveStatus

class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False) # Store company ID from session
    
    company = db.relationship("CompanyProfile")
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.String(500), nullable=False)
    job_location = db.Column(db.String(100), nullable=False)
    package_amount = db.Column(db.String(50), nullable=False)
    
    application_deadline = db.Column(db.DateTime, nullable=False)
    
    approval_status = db.Column(db.String(20), default="Pending")
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Drive {self.job_title} - {self.approval_status}>"
