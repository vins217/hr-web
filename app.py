from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Employee, Attendance, Payroll
from config import Config
from payroll import compute_payroll_for_period
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def ensure_db():
    with app.app_context():
        db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

# Employees
@app.route("/employees", methods=["GET", "POST"])
def employees():
    if request.method == "POST":
        f = request.form
        try:
            emp = Employee(
                first_name=f.get("first_name","").strip(),
                last_name=f.get("last_name","").strip(),
                monthly_salary=float(f.get("monthly_salary", "0") or 0),
                tin=f.get("tin","").strip(),
                sss=f.get("sss","").strip(),
                philhealth=f.get("philhealth","").strip(),
                pagibig=f.get("pagibig","").strip(),
            )
            if not emp.first_name or not emp.last_name:
                raise ValueError("First/Last name required.")
            db.session.add(emp); db.session.commit()
            flash("Employee added.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
        return redirect(url_for("employees"))
    emps = Employee.query.order_by(Employee.id.desc()).all()
    return render_template("employees.html", employees=emps)

# Attendance
@app.route("/attendance", methods=["GET","POST"])
def attendance():
    emps = Employee.query.order_by(Employee.id).all()
    if request.method == "POST":
        f = request.form
        try:
            emp_id = int(f.get("employee_id"))
            date = f.get("date")
            time_in = f.get("time_in")
            time_out = f.get("time_out")
            # basic validation
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time_in, "%H:%M")
            datetime.strptime(time_out, "%H:%M")
            rec = Attendance(employee_id=emp_id, date=date, time_in=time_in, time_out=time_out)
            db.session.add(rec); db.session.commit()
            flash("Attendance saved.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
        return redirect(url_for("attendance"))
    recent = Attendance.query.order_by(Attendance.id.desc()).limit(50).all()
    return render_template("attendance.html", employees=emps, recent=recent)

# Payroll
@app.route("/payroll", methods=["GET", "POST"])
def payroll():
    emps = Employee.query.order_by(Employee.id).all()
    result = None
    history = []
    if request.method == "POST":
        f = request.form
        try:
            emp_id = int(f.get("employee_id"))
            start = f.get("start"); end = f.get("end")
            # Pull employee & attendance
            emp = Employee.query.get(emp_id)
            if not emp: raise ValueError("Employee not found.")
            daily_rate = float(emp.monthly_salary) / 22.0
            rows = Attendance.query.filter(Attendance.employee_id==emp_id, Attendance.date>=start, Attendance.date<=end).order_by(Attendance.date).all()
            if not rows: raise ValueError("No attendance in that period.")
            summary = compute_payroll_for_period(daily_rate, [dict(date=r.date, time_in=r.time_in, time_out=r.time_out) for r in rows])
            # Save
            p = Payroll(
                employee_id=emp_id, period_start=start, period_end=end,
                gross_pay=summary["gross"], sss_contrib=summary["sss"],
                philhealth_contrib=summary["philhealth"], pagibig_contrib=summary["pagibig"],
                tax_withheld=summary["tax"], net_pay=summary["net"]
            )
            db.session.add(p); db.session.commit()
            result = summary
            flash("Payroll computed & saved.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
    # history (optionally filter by employee_id)
    q_emp = request.args.get("emp")
    if q_emp:
        try:
            emp_id = int(q_emp)
            history = Payroll.query.filter(Payroll.employee_id==emp_id).order_by(Payroll.id.desc()).all()
        except:
            history = Payroll.query.order_by(Payroll.id.desc()).limit(50).all()
    else:
        history = Payroll.query.order_by(Payroll.id.desc()).limit(50).all()
    return render_template("payroll.html", employees=emps, result=result, history=history)

if __name__ == "__main__":
    ensure_db()
    # Dev server (for local test). On cloud, use gunicorn via Procfile.
    app.run(host="0.0.0.0", port=5000, debug=True)
