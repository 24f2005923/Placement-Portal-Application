from database import db

class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), unique=True, nullable=False)

    full_name = db.Column(db.String(255), nullable=False)
    university_register_number = db.Column(db.String(100), unique=True, nullable=False)
    gender_code = db.Column(db.String(20), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)

    institutional_email = db.Column(db.String(255), unique=True, nullable=False)
    personal_email = db.Column(db.String(255), nullable=True)
    primary_phone = db.Column(db.String(20), nullable=False)
    secondary_phone = db.Column(db.String(20), nullable=True)

    skills = db.Column(db.String(500), nullable=True)
    cv_filename = db.Column(db.String(255), nullable=True)
    profile_completion_score = db.Column(db.Integer, default=0)

    def __repr__(self) -> str:
        return f"<StudentProfile name={self.full_name} reg_no={self.university_register_number}>"
