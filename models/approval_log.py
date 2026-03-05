from datetime import datetime, timezone
from database import db
from models.enums import AccountState

class ApprovalLog(db.Model):
    __tablename__ = "approval_logs"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    
    previous_state = db.Column(db.Enum(AccountState), nullable=False)
    new_state = db.Column(db.Enum(AccountState), nullable=False)
    
    timestamp = db.Column(
        db.DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )

    target_account = db.relationship("Account", foreign_keys=[account_id])
    admin_account = db.relationship("Account", foreign_keys=[admin_id])

    def __repr__(self) -> str:
        return f"<ApprovalLog account={self.account_id} transition={self.previous_state.value}->{self.new_state.value}>"
