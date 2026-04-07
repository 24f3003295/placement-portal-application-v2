from flask import Flask, render_template
from models import User,Company,JobPosition,Student,Application,Placement,db
from auth import auth_bp
from utils import role_required
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from datetime import timedelta

app = Flask(__name__,)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)

db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/api')

# CREATE DB + ADMIN
with app.app_context():
    db.create_all()

    # Create Admin if not exists
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin_user = User(
            name="Admin",
            email="admin@ppa.com",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created")

# Routes
@app.route('/')
def home():
    return render_template('login.html') 

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/student')
def student_page():
    return render_template('student.html')

@app.route('/company')
def company_page():
    return render_template('company.html')


@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    return {"msg": "Admin"}

@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    return {"msg": "Student"}



# Admin Dashboard
# Admin Stats API
@app.route('/admin/stats', methods=['GET'])
@role_required('admin')
def admin_stats():
    from models import Student, Company, Job, Application

    return {
        "students": Student.query.count(),
        "companies": Company.query.count(),
        "jobs": Job.query.count(),
        "applications": Application.query.count()
    }

# Search Companies
@app.route('/admin/companies', methods=['GET'])
@role_required('admin')
def get_companies():
    from models import Company, User
    from flask import request

    search = request.args.get('search', '')

    if search:
        companies = Company.query.join(User).filter(
            Company.company_name.ilike(f"%{search}%") |
            User.name.ilike(f"%{search}%")
        ).all()
    else:
        companies = Company.query.all()

    return [{
        "id": c.id,
        "company_name": c.company_name,
        "approval_status": c.approval_status,
        "is_blacklisted": c.is_blacklisted,
        "email": c.user.email if c.user else "",
        "name": c.user.name if c.user else ""   # <-- added
    } for c in companies]

@app.route('/admin/company/<int:id>/approve', methods=['PUT'])
@role_required('admin')
def approve_company(id):
    from models import Company
    from app import db

    company = Company.query.get(id)

    if not company:
        return {"error": "Company not found"}, 404

    company.approval_status = "approved"  
    db.session.commit()

    return {"msg": "Company approved"}


# Delete Company
@app.route('/admin/company/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_company(id):
    from models import Company
    from app import db

    company = Company.query.get(id)
    if not company:
        return {"error": "Company not found"}, 404

    db.session.delete(company)
    db.session.commit()

    return {"msg": "Company deleted"}

# Deactivate Company (Blacklist)
@app.route('/admin/company/<int:id>/deactivate', methods=['PUT'])
@role_required('admin')
def deactivate_company(id):
    from models import Company
    from app import db

    company = Company.query.get(id)
    if not company:
        return {"error": "Company not found"}, 404

    company.is_active = False
    db.session.commit()

    return {"msg": "Company deactivated"}

# Search Students
@app.route('/admin/students', methods=['GET'])
@role_required('admin')
def get_students():
    from models import Student

    search = request.args.get('search', '')

    students = Student.query.filter(
        Student.name.ilike(f"%{search}%")
    ).all()

    return [{
        "id": s.id,
        "name": s.name,
        "email": s.email,
        "is_active": s.is_active
    } for s in students]

# Deactivate Student
@app.route('/admin/student/<int:id>/deactivate', methods=['PUT'])
@role_required('admin')
def deactivate_student(id):
    from models import Student
    from app import db

    s = Student.query.get(id)
    if not s:
        return {"error": "Student not found"}, 404

    s.is_active = False
    db.session.commit()

    return {"msg": "Student deactivated"}

# Get Jobs with approval status
@app.route('/admin/jobs', methods=['GET'])
@role_required('admin')
def get_jobs():
    from models import Job

    jobs = Job.query.all()

    return [{
        "id": j.id,
        "title": j.title,
        "company_id": j.company_id,
        "approval_status": j.approval_status
    } for j in jobs]

# Approve Job
@app.route('/admin/job/<int:id>/approve', methods=['PUT'])
@role_required('admin')
def approve_job(id):
    from models import Job
    from app import db

    job = Job.query.get(id)
    if not job:
        return {"error": "Job not found"}, 404

    job.approval_status = "approved"
    db.session.commit()

    return {"msg": "Job approved"}

# Delete Job
@app.route('/admin/job/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_job(id):
    from models import Job
    from app import db

    job = Job.query.get(id)
    if not job:
        return {"error": "Job not found"}, 404

    db.session.delete(job)
    db.session.commit()

    return {"msg": "Job deleted"}


# Get Applications
@app.route('/admin/applications', methods=['GET'])
@role_required('admin')
def get_applications():
    from models import Application

    apps = Application.query.all()

    return [{
        "id": a.id,
        "student_id": a.student_id,
        "job_id": a.job_id,
        "status": a.status
    } for a in apps]

# Approve Application
@app.route('/admin/application/<int:id>/approve', methods=['PUT'])
@role_required('admin')
def approve_application(id):
    from models import Application
    from app import db

    app_obj = Application.query.get(id)
    if not app_obj:
        return {"error": "Application not found"}, 404

    app_obj.status = "approved"
    db.session.commit()

    return {"msg": "Application approved"}

# Delete Application
@app.route('/admin/application/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_application_admin(id):

    from models import Application
    from app import db

    app_obj = Application.query.get(id)
    if not app_obj:
        return {"error": "Application not found"}, 404

    db.session.delete(app_obj)
    db.session.commit()

    return {"msg": "Application deleted"}

# Company Dashboard
# Companies will register their profile.
@app.route('/company/register', methods=['POST'])
def company_register():
    from models import User, Company
    from app import db
    from flask import request

    data = request.json

    # Check if user already exists
    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return {"error": "Email already registered"}, 400

    # Create User
    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),  
        role="company"
    )

    db.session.add(user)
    db.session.commit()  # commit to get user.id

    # Create Company Profile
    company = Company(
        user_id=user.id,
        company_name=data['company_name'],
        industry=data['industry'],
        location=data['location'],
        website=data['website'],
        approval_status="pending",
        is_blacklisted=False
    )

    db.session.add(company)
    db.session.commit()

    return {"msg": "Company registered. Waiting for admin approval"}

# Companies can only access the dashboard when approved by admin.
def check_company_access():
    from models import Company
    from flask_jwt_extended import get_jwt_identity

    user_id = get_jwt_identity()

    company = Company.query.filter_by(user_id=user_id).first()

    if not company:
        return None, {"error": "Company not found"}, 404

    if company.approval_status != "approved":
        return None, {"error": "Not approved"}, 403

    if getattr(company, "is_blacklisted", False):
        return None, {"error": "Blacklisted"}, 403

    return company, None, None


# Dashboard showing job postings, received applications, and shortlisted candidates.
@app.route('/company/dashboard', methods=['GET'])
@role_required('company')
def company_dashboard():
    from models import JobPosition, Application

    # Use reusable check
    company, err, code = check_company_access()
    if err:
        return err, code

    company_id = company.id

    jobs = JobPosition.query.filter_by(company_id=company_id).all()

    applications = Application.query.join(JobPosition).filter(
        JobPosition.company_id == company_id
    ).all()

    shortlisted = [a for a in applications if a.status == "shortlisted"]

    return {
        "jobs": [{
            "id": j.id,
            "title": j.title,
            "is_active": j.is_active
        } for j in jobs],

        "applications": [{
            "id": a.id,
            "student_id": a.student_id,
            "job_id": a.job_id,
            "status": a.status
        } for a in applications],

        "shortlisted": [{
            "id": a.id,
            "student_id": a.student_id,
            "job_id": a.job_id
        } for a in shortlisted]
    }


# Post New Job
@app.route('/company/job', methods=['POST'])
@role_required('company')
def create_job():
    from models import JobPosition
    from app import db
    from flask import request
    from flask_jwt_extended import get_jwt_identity

    data = request.json
    company, err, code = check_company_access()
    if err:
        return err, code
    company_id = company.id

    job = JobPosition(
        title=data.get('title'),
        skills_required=data.get('skills_required'),
        experience=data.get('experience'),
        salary=float(data.get('salary').replace(",", "")),
        company_id=company_id,
        is_active=True,
        status="pending",
        is_approved=False
    )


    db.session.add(job)
    db.session.commit()

    return {"msg": "Job created, waiting for admin approval"}

# View Applications for a job
@app.route('/company/job/<int:id>/applications', methods=['GET'])
@role_required('company')
def get_job_applications(id):
    from models import Application

    company, err, code = check_company_access()
    if err:
        return err, code

    job = JobPosition.query.get(id)
    if job.company_id != company.id:
        return {"error": "Unauthorized"}, 403

    apps = Application.query.filter_by(job_id=id).all()

    return [{
        "id": a.id,
        "student_id": a.student_id,
        "status": a.status
    } for a in apps]

# Delete Application
@app.route('/company/application/<int:id>', methods=['DELETE'])
@role_required('company')
def delete_application_company(id):
    
    from app import db

    company, err, code = check_company_access()
    if err:
        return err, code

    app_obj = Application.query.get(id)
    if not app_obj:
        return {"error": "Not found"}, 404

    job = JobPosition.query.get(app_obj.job_id)
    if job.company_id != company.id:
        return {"error": "Unauthorized"}, 403

    db.session.delete(app_obj)
    db.session.commit()

    return {"msg": "Application deleted"}

# Shortlist/Reject/Select
@app.route('/company/application/<int:id>/update', methods=['PUT'])
@role_required('company')
def update_application(id):
    
    from app import db
    from flask import request
    from flask_jwt_extended import get_jwt_identity

    company, err, code = check_company_access()
    if err:
        return err, code
    
    company_id = company.id

    data = request.json

    valid_status = ["shortlisted", "selected", "rejected"]

    if data.get("status") not in valid_status:
        return {"error": "Invalid status"}, 400

    app_obj = Application.query.get(id)
    if not app_obj:
        return {"error": "Application not found"}, 404

    # SECURITY CHECK 
    job = JobPosition.query.get(app_obj.job_id)
    if job.company_id != company_id:
        return {"error": "Unauthorized"}, 403

    # Update
    app_obj.status = data.get("status")
    app_obj.feedback = data.get("feedback")

    db.session.commit()

    return {"msg": f"Application marked as {app_obj.status}"}


# Close/open job
@app.route('/company/job/<int:id>/toggle', methods=['PUT'])
@role_required('company')
def toggle_job(id):
    
    from app import db

    company, err, code = check_company_access()
    if err:
        return err, code

    job = JobPosition.query.get(id)
    if not job:
        return {"error": "Job not found"}, 404

    if job.company_id != company.id:
        return {"error": "Unauthorized"}, 403

    job.is_active = not job.is_active
    db.session.commit()

    return {"msg": "Job status updated"}

# Schedule Interviews with shortlisted candidates
@app.route('/company/application/<int:id>/schedule', methods=['PUT'])
@role_required('company')
def schedule_interview(id):
    from models import Application
    from app import db
    from flask import request

    data = request.json

    company, err, code = check_company_access()
    if err:
        return err, code

    app_obj = Application.query.get(id)
    job = JobPosition.query.get(app_obj.job_id)

    if job.company_id != company.id:
        return {"error": "Unauthorized"}, 403

    
    if not app_obj:
        return {"error": "Application not found"}, 404

    if app_obj.status != "shortlisted":
        return {"error": "Only shortlisted candidates can be scheduled"}, 400

    app_obj.interview_date = data.get("date")
    app_obj.interview_location = data.get("location")

    db.session.commit()

    return {"msg": "Interview scheduled successfully"}


if __name__ == "__main__":
    app.run(debug=True)
