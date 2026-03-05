from database import db
from models import Account, ApprovalLog
from models.enums import AccountState

def verify_student_account(admin_id, student_account_id, action):
    """
    Handles transition of student account from PENDING_VERIFICATION to ACTIVE or REJECTED.
    Ensures state transition validation and logs the action.
    """
    student_account = Account.query.get(student_account_id)
    if not student_account:
        raise ValueError("Student account not found.")

    if student_account.account_state != AccountState.PENDING_VERIFICATION:
        raise ValueError(f"Invalid state transition. Current state: {student_account.account_state.value}")

    if action == "approve":
        new_state = AccountState.ACTIVE
    elif action == "reject":
        new_state = AccountState.REJECTED
    else:
        raise ValueError(f"Invalid action: {action}")

    old_state = student_account.account_state

    student_account.account_state = new_state
    
    log_entry = ApprovalLog(
        account_id=student_account_id,
        admin_id=admin_id,
        previous_state=old_state,
        new_state=new_state
    )
    
    db.session.add(log_entry)
    db.session.commit()
    
    return student_account
def verify_company_account(admin_id, company_account_id, action):
    """
    Handles transition of company account from PENDING_VERIFICATION to ACTIVE or REJECTED.
    Ensures state transition validation and logs the action.
    """
    company_account = Account.query.get(company_account_id)
    if not company_account:
        raise ValueError("Company account not found.")

    if company_account.account_state != AccountState.PENDING_VERIFICATION:
        raise ValueError(f"Invalid state transition. Current state: {company_account.account_state.value}")

    if action == "approve":
        new_state = AccountState.ACTIVE
    elif action == "reject":
        new_state = AccountState.REJECTED
    else:
        raise ValueError(f"Invalid action: {action}")

    old_state = company_account.account_state

    company_account.account_state = new_state
    
    log_entry = ApprovalLog(
        account_id=company_account_id,
        admin_id=admin_id,
        previous_state=old_state,
        new_state=new_state
    )
    
    db.session.add(log_entry)
    db.session.commit()
    
    return company_account
