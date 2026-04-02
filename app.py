from flask import Flask, render_template
from models import *
from auth import auth_bp
from utils import role_required
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash


app = Flask(__name__,)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

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
    return render_template('index.html')

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

@app.route('/company/dashboard')
@role_required('company')
def company_dashboard():
    return {"msg": "Company"}

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
from flask import request

@app.route('/admin/companies', methods=['GET'])
@role_required('admin')
def get_companies():
    from models import Company

    search = request.args.get('search', '')

    companies = Company.query.filter(
        Company.name.ilike(f"%{search}%")
    ).all()

    return [{
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "is_approved": c.is_approved,
        "is_active": c.is_active
    } for c in companies]

# Approve Company
@app.route('/admin/company/<int:id>/approve', methods=['PUT'])
@role_required('admin')
def approve_company(id):
    from models import Company
    from app import db

    company = Company.query.get(id)
    if not company:
        return {"error": "Company not found"}, 404

    company.is_approved = True
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
        "is_approved": j.is_approved
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

    job.is_approved = True
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
def delete_application(id):
    from models import Application
    from app import db

    app_obj = Application.query.get(id)
    if not app_obj:
        return {"error": "Application not found"}, 404

    db.session.delete(app_obj)
    db.session.commit()

    return {"msg": "Application deleted"}

if __name__ == "__main__":
    app.run(debug=True)
