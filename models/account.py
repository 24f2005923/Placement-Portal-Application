from datetime import datetime

from database import db
from models.enums import AccountRole, AccountState

class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)

    login_identifier = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), nullable=False)
    account_state = db.Column(
        db.String(50),
        nullable=False,
        default=AccountState.PENDING_VERIFICATION.value,
    )

    student_profile = db.relationship("StudentProfile", backref="account", lazy=True, uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship("CompanyProfile", backref="account", lazy=True, uselist=False, cascade="all, delete-orphan")

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now,
    )
    last_login_at = db.Column(db.DateTime, nullable=True)

    def is_active(self) -> bool:
        return self.account_state == AccountState.ACTIVE.value

    def record_login(self):
        self.last_login_at = datetime.now()

    def __repr__(self) -> str:
        return f"<Account id={self.id} role={self.role} state={self.account_state}>"

    @property
    def is_blacklisted(self) -> bool:
        from models.blacklist_entry import BlacklistEntry
        if self.role == 'student':
            entity_id = self.student_profile.id if self.student_profile else self.id
            return BlacklistEntry.query.filter_by(entity_type='student', entity_id=entity_id).first() is not None
        elif self.role == 'company':
            entity_id = self.company_profile.id if self.company_profile else self.id
            return BlacklistEntry.query.filter_by(entity_type='company', entity_id=entity_id).first() is not None
        return False
