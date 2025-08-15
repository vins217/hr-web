from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    monthly_salary = db.Column(db.Float, nullable=False)
    tin = db.Column(db.String(32))
    sss = db.Column(db.String(32))
    philhealth = db.Column(db.String(32))
    pagibig = db.Column(db.String(32))

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    date = db.Column(db.String(10), nullable=False)      # YYYY-MM-DD
    time_in = db.Column(db.String(5), nullable=False)    # HH:MM
    time_out = db.Column(db.String(5), nullable=False)   # HH:MM
    employee = db.relationship("Employee", backref=db.backref("attendance", lazy=True))

class Payroll(db.Model):
    __tablename__ = "payroll"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)
    period_start = db.Column(db.String(10), nullable=False)
    period_end = db.Column(db.String(10), nullable=False)
    gross_pay = db.Column(db.Float, nullable=False)
    sss_contrib = db.Column(db.Float, nullable=False)
    philhealth_contrib = db.Column(db.Float, nullable=False)
    pagibig_contrib = db.Column(db.Float, nullable=False)
    tax_withheld = db.Column(db.Float, nullable=False)
    net_pay = db.Column(db.Float, nullable=False)
    employee = db.relationship("Employee", backref=db.backref("payrolls", lazy=True))
