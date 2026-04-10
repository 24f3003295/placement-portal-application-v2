from celery_worker import make_celery
from models import Application, Student, User
from datetime import datetime, timedelta
import pandas as pd
from app import app
celery = make_celery(app)

# Interview Reminder
@celery.task(name='task.send_single_reminder')
def send_single_reminder(app_id):
    from models import Application, Student, User
    from app import app, mail
    from flask_mail import Message

    with app.app_context():

        a = Application.query.get(app_id)

        if not a or not a.interview_date:
            return "No interview scheduled"

        student = Student.query.get(a.student_id)
        user = User.query.get(student.user_id)

        print("SENDING FOR APP:", a.id)
        print("EMAIL:", user.email)
        print("DATE:", a.interview_date)

        msg = Message(
            subject="Interview Reminder",
            sender=app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )

        msg.body = f"""
Hi {user.name},

You have an interview scheduled.

📅 Date: {a.interview_date}
📍 Location: {a.interview_location}

Good luck!
PlacementHub Team
"""

        mail.send(msg)

        return f"Sent to {user.email}"

# Placement Report(Monthly)
@celery.task
def generate_monthly_report():
    from models import Application, Company
    import os
    from datetime import datetime
    from flask import current_app

    base_dir = current_app.root_path

    reports_dir = os.path.join(base_dir, "static", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    file_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    file_path = os.path.join(reports_dir, file_name)

    relative_path = f"static/reports/{file_name}"

    companies = Company.query.all()

    rows = ""
    total_companies = len(companies)
    total_apps_all = 0

    for c in companies:
        apps = Application.query.join(Application.job)\
            .filter_by(company_id=c.id).all()

        total = len(apps)
        selected = len([a for a in apps if a.status == "selected"])
        rate = (selected / total * 100) if total > 0 else 0

        total_apps_all += total

        rows += f"""
        <tr>
            <td>{c.company_name}</td>
            <td>{total}</td>
            <td>{selected}</td>
            <td>{rate:.2f}%</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Placement Report</title>

        <!-- ✅ Use same dashboard CSS -->
        <link rel="stylesheet" href="/static/portal.css">

        <!-- minimal spacing fix -->
        <style>
            body {{
                padding: 40px;
            }}
        </style>
    </head>

    <body>

    <div class="page-content" style="max-width:1000px; margin:auto">

        <!-- Header -->
        <div class="card" style="margin-bottom:20px">
            <div class="card-header">
                <span class="section-title">📊 Placement Report</span>
            </div>
            <div style="padding:16px; font-size:13px; color:var(--text-muted)">
                Generated on: {timestamp}
            </div>
        </div>

        <!-- Stats -->
        <div class="grid-2" style="margin-bottom:20px">
            <div class="card">
                <div class="section-title">🏢 Companies</div>
                <div style="font-size:20px; font-weight:700">{total_companies}</div>
            </div>

            <div class="card">
                <div class="section-title">📄 Applications</div>
                <div style="font-size:20px; font-weight:700">{total_apps_all}</div>
            </div>
        </div>

        <!-- Table -->
        <div class="card">
            <div class="card-header">
                <span class="section-title">Report Details</span>
            </div>

            <div style="padding:16px">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Company</th>
                            <th>Total Applications</th>
                            <th>Selected</th>
                            <th>Success Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>

    </div>

    </body>
    </html>
    """

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return relative_path

# User Triggered CSV Export for student
@celery.task(bind=True)
def export_student_csv(self, student_id):
    try:
        from models import Application
        import os
        import pandas as pd
        from flask import current_app

        # ✅ Absolute project path
        base_dir = current_app.root_path

        # ✅ Correct export folder path
        export_dir = os.path.join(base_dir, "static", "exports")

        # 🔥 FORCE create directory
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        print("📁 Export directory:", export_dir)

        apps = Application.query.filter_by(student_id=student_id).all()

        data = []
        for a in apps:
            data.append({
                "job": a.job.title if a.job else "N/A",
                "status": a.status,
                "date": str(a.applied_date)
            })

        df = pd.DataFrame(data)

        # ✅ FULL ABSOLUTE PATH
        file_name = f"student_{student_id}.csv"
        file_path = os.path.join(export_dir, file_name)

        print("📄 Saving file at:", file_path)

        df.to_csv(file_path, index=False)

        return f"static/exports/{file_name}"

    except Exception as e:
        print("❌ EXPORT ERROR:", str(e))
        return "ERROR"

# User Triggered CSV Export for company
@celery.task(bind=True)
def export_company_csv(self, company_id):
    try:
        from models import Application, JobPosition, Student
        import os
        import pandas as pd
        from flask import current_app

        base_dir = current_app.root_path
        export_dir = os.path.join(base_dir, "static", "exports")
        os.makedirs(export_dir, exist_ok=True)

        jobs = JobPosition.query.filter_by(company_id=company_id).all()
        job_ids = [j.id for j in jobs]

        if not job_ids:
            return "ERROR"

        apps = Application.query.filter(Application.job_id.in_(job_ids)).all()

        data = []
        for a in apps:
            student = Student.query.get(a.student_id)
            job = JobPosition.query.get(a.job_id)

            # ✅ FIX HERE
            name = student.user.name if student and student.user else "N/A"
            email = student.user.email if student and student.user else "N/A"

            data.append({
                "student_name": name,
                "student_email": email,
                "job_title": job.title if job else "N/A",
                "status": a.status,
                "applied_date": str(a.applied_date)
            })

        df = pd.DataFrame(data)

        file_name = f"company_{company_id}.csv"
        file_path = os.path.join(export_dir, file_name)

        df.to_csv(file_path, index=False)

        return f"static/exports/{file_name}"

    except Exception as e:
        print("❌ COMPANY EXPORT ERROR:", str(e))
        return "ERROR"
