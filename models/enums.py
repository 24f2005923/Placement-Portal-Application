import enum


class AccountRole(enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    COMPANY = "company"


class AccountState(enum.Enum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
