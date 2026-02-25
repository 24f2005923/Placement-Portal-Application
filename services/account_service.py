from database import db
from models import Account, ApprovalLog
from models.enums import AccountState

def verify_student_account(admin_id, student_account_id, action):
    """
    Handles transition of student account from PENDING_VERIFICATION to ACTIVE or REJECTED.
    Ensures state transition validation and logs the action.
    """
    # Fetch target student account
    student_account = Account.query.get(student_account_id)
    if not student_account:
        raise ValueError("Student account not found.")

    # Validation: Only allow processing from PENDING_VERIFICATION
    if student_account.account_state != AccountState.PENDING_VERIFICATION:
        raise ValueError(f"Invalid state transition. Current state: {student_account.account_state.value}")

    # Determine new state based on action
    if action == "approve":
        new_state = AccountState.ACTIVE
    elif action == "reject":
        new_state = AccountState.REJECTED
    else:
        raise ValueError(f"Invalid action: {action}")

    # Capture previous state for logging
    old_state = student_account.account_state

    # Perform transition
    student_account.account_state = new_state
    
    # Create ApprovalLog entry
    log_entry = ApprovalLog(
        account_id=student_account_id,
        admin_id=admin_id,
        previous_state=old_state,
        new_state=new_state
    )
    
    db.session.add(log_entry)
    db.session.commit()
    
    return student_account
