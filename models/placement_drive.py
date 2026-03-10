from datetime import datetime
from database import db
from models.enums import DriveStatus

class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)
    
    company = db.relationship("CompanyProfile")
    job_title = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.String(500), nullable=False)
    job_location = db.Column(db.String(100), nullable=False)
    package_amount = db.Column(db.String(50), nullable=False)
    
    application_deadline = db.Column(db.DateTime, nullable=False)
    
    approval_status = db.Column(
        db.Enum(DriveStatus),
        nullable=False,
        default=DriveStatus.PENDING
    )
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    rejection_reason = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Drive {self.job_title} - {self.approval_status}>"

    @property
    def is_blacklisted(self) -> bool:
        from models.blacklist_entry import BlacklistEntry
        is_drive_blacklisted = BlacklistEntry.query.filter_by(entity_type='drive', entity_id=self.id).first() is not None
        if is_drive_blacklisted:
            return True
        if self.company_id:
            return BlacklistEntry.query.filter_by(entity_type='company', entity_id=self.company_id).first() is not None
        return False
