# Simple payroll computation logic (demo rates)
def compute_payroll_for_period(daily_rate, attendance_rows):
    # attendance_rows: list of dicts: {date, time_in, time_out}
    # tardiness vs 08:00 start
    from datetime import datetime
    total_days = len(attendance_rows)
    tardy_minutes = 0
    for row in attendance_rows:
        sched = datetime.strptime(row["date"] + " 08:00", "%Y-%m-%d %H:%M")
        actual = datetime.strptime(row["date"] + " " + row["time_in"], "%Y-%m-%d %H:%M")
        if actual > sched:
            tardy_minutes += int((actual - sched).total_seconds() // 60)
    hourly = daily_rate / 8.0
    tardy_ded = (tardy_minutes/60.0) * hourly
    gross = (daily_rate * total_days) - tardy_ded
    sss = gross * 0.045
    phil = gross * 0.025
    pagibig = gross * 0.01
    taxable = gross - (sss + phil + pagibig)
    tax = taxable * 0.10
    net = taxable - tax
    return {
        "days": total_days,
        "tardy_minutes": tardy_minutes,
        "gross": round(gross,2),
        "sss": round(sss,2),
        "philhealth": round(phil,2),
        "pagibig": round(pagibig,2),
        "tax": round(tax,2),
        "net": round(net,2),
    }
