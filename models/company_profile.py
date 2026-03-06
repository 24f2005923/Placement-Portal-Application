from database import db

class CompanyProfile(db.Model):
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), unique=True, nullable=False)

    name = db.Column(db.String(255), nullable=False)
    company_id_field = db.Column(db.String(100), unique=True, nullable=False) # Matches template
    website_url = db.Column(db.String(255), nullable=True)
    industry_type = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)

    hr_contact = db.Column(db.String(255), nullable=False)
    work_email = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<CompanyProfile name={self.name} reg_id={self.company_id_field}>"
