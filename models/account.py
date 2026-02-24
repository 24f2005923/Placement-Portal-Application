from datetime import datetime, timezone

from sqlalchemy import Enum as SAEnum

from database import db
from models.enums import AccountRole, AccountState


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)

    login_identifier = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(
        SAEnum(AccountRole, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    account_state = db.Column(
        SAEnum(AccountState, values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=AccountState.PENDING_VERIFICATION,
    )

    # Relationships
    student_profile = db.relationship("StudentProfile", back_populates="account", uselist=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def record_login(self):
        self.last_login_at = datetime.now(timezone.utc)

    def is_active(self) -> bool:
        return self.account_state == AccountState.ACTIVE

    def __repr__(self) -> str:
        return f"<Account id={self.id} role={self.role.value} state={self.account_state.value}>"
