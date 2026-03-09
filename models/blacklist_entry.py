from datetime import datetime
from database import db

class BlacklistEntry(db.Model):
    __tablename__ = "blacklist_entries"

    id = db.Column(db.Integer, primary_key=True)
    entity_type = db.Column(db.String(50), nullable=False)  # student, company, drive, application
    entity_id = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(500), nullable=True)
    
    blacklisted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    
    admin = db.relationship("Account", backref=db.backref("blacklist_actions", lazy=True))

    def __repr__(self) -> str:
        return f"<BlacklistEntry type={self.entity_type} id={self.entity_id}>"
