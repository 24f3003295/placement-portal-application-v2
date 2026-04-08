from flask import Flask, render_template, request
from models import User,Company,JobPosition,Student,Application,Placement,db
from auth import auth_bp
from utils import role_required
from flask_jwt_extended import JWTManager,jwt_required, get_jwt_identity
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
    from models import Student, Company, JobPosition, Application

    return {
        "students": Student.query.count(),
        "companies": Company.query.count(),
        "jobs": JobPosition.query.count(),
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

# Deactivate Company
@app.route('/admin/company/<int:id>/deactivate', methods=['PUT'])
@role_required('admin')
def deactivate_company(id):
    from models import Company
    from app import db

    company = db.session.get(Company, id)
    
    if not company:
        return {"error": "Company not found"}, 404

    # Toggle the status
    company.is_blacklisted = not company.is_blacklisted
    
    # Determine the message based on the new state
    if company.is_blacklisted:
        message = "Company deactivated and blacklisted."
    else:
        message = "Company reactivated successfully."
    
    try:
        db.session.commit()
        # Return the dynamic message
        return {"msg": message}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    
# Search Students
@app.route('/admin/students', methods=['GET'])
@role_required('admin')
def get_students():
    search = request.args.get('search', '')

    query = db.session.query(Student, User).join(User, Student.user_id == User.id)

    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))

    results = query.all()

    return [{
        "id": student.id,
        "name": user.name,
        "email": user.email,
        "is_blacklisted": student.is_blacklisted,
        "branch": student.branch,
        "cgpa": student.cgpa
    } for student, user in results]

# Deactivate Student
@app.route('/admin/student/<int:id>/deactivate', methods=['PUT'])
@role_required('admin')
def deactivate_student(id):
    from models import Student
    from app import db

    # Using session.get (preferred)
    s = db.session.get(Student, id)
    
    if not s:
        return {"error": "Student not found"}, 404

    # Toggle the status: True becomes False, False becomes True
    s.is_blacklisted = not s.is_blacklisted
    
    # Determine the message based on the new status
    if s.is_blacklisted:
        message = "Student account has been deactivated."
    else:
        message = "Student account has been activated."

    try:
        db.session.commit()
        return {"msg": message}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

# Get Jobs with approval status
@app.route('/admin/jobs', methods=['GET'])
@role_required('admin')
def get_jobs():
    from models import JobPosition

    jobs = JobPosition.query.all()

    return [{
        "id": j.id,
        "title": j.title,
        "company_id": j.company_id,
        "is_approved": "approved" if j.is_approved else "not approved"
    } for j in jobs]

# Approve Job
@app.route('/admin/job/<int:id>/approve', methods=['PUT'])
@role_required('admin')
def approve_job(id):
    
    from app import db

    job = JobPosition.query.get(id)
    if not job:
        return {"error": "Job not found"}, 404

    job.is_approved = True
    db.session.commit()

    return {"msg": "Job approved"}

# Delete Job
@app.route('/admin/job/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_job(id):
    from app import db

    job = JobPosition.query.get(id)
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
    app_obj = db.session.get(Application, id)
    
    if not app_obj:
        return {"error": "Application not found"}, 404

    try:
        db.session.delete(app_obj)
        db.session.commit()
        return {"msg": "Application deleted"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
    
# Company Dashboard
# Companies will register their profile.
@app.route('/company/register', methods=['POST'])
def company_register():
    from models import User, Company
    from app import db
    from flask import request
    from werkzeug.security import generate_password_hash

    data = request.get_json()

    try:
        # 1. Validation
        if User.query.filter_by(email=data.get('email')).first():
            return {"error": "Email already registered"}, 400

        # 2. Stage the User
        user = User(
            email=data['email'],
            password=generate_password_hash(data['password']),  
            role="company"
        )
        db.session.add(user)
        
        # flush() sends the SQL to the DB and gets the ID back, 
        # but doesn't "lock it in" yet.
        db.session.flush() 

        # 3. Stage the Company
        company = Company(
            user_id=user.id,
            company_name=data.get('company_name'),
            industry=data.get('industry'),
            location=data.get('location'),
            website=data.get('website'),
            approval_status="pending",
            is_blacklisted=False
        )
        db.session.add(company)

        # 4. Final Commit (Saves BOTH or NEITHER)
        db.session.commit()
        return {"msg": "Company registered. Waiting for admin approval"}, 201

    except Exception as e:
        db.session.rollback() # This is crucial! It undoes the User creation if Company fails.
        print(f"Error: {e}") # Check your terminal to see the EXACT error (e.g., column length)
        return {"error": "Internal Server Error"}, 500
    
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

# Upload Offer Letter if Status is Selected
import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from models import Application, JobPosition, Company
from app import db # Assuming db is initialized in app.py

# Configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'offers')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/company/application/<int:id>/update', methods=['PUT'])
@jwt_required()
def update_application(id):
    # 1. Access Check
    company, err, code = check_company_access()
    if err: return err, code

    app_obj = Application.query.get(id)
    if not app_obj:
        return {"error": "Application not found"}, 404

    status = request.form.get("status") or (request.json.get("status") if request.json else None)
    feedback = request.form.get("feedback") or (request.json.get("feedback", "") if request.json else "")

    if not status:
        return {"error": "Status is required"}, 400

    if status == "selected":
        if 'offer_letter' not in request.files:
            return {"error": "No file uploaded"}, 400
        
        file = request.files['offer_letter']
        if file.filename == '':
            return {"error": "No file selected"}, 400

        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(f"offer_app_{id}.pdf")
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            
            file.save(save_path)
            
            app_obj.offer_letter = f"static/uploads/offers/{filename}"
            app_obj.status = "selected"
        else:
            return {"error": "Only PDF files allowed"}, 400
    else:
        app_obj.status = status

    app_obj.feedback = feedback
    db.session.commit()

    return {"msg": f"Application updated to {app_obj.status}"}

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

# Student Dashboard
# STUDENT REGISTER
@app.route('/student/register', methods=['POST'])
def  student_register():
    from models import User, Student
    from app import db
    from flask import request
    from werkzeug.security import generate_password_hash

    data = request.json

    if User.query.filter_by(email=data['email']).first():
        return {"error": "Email already exists"}, 400

    user = User(
        name=data.get('name'),
        email=data.get('email'),
        password=generate_password_hash(data.get('password')),
        role="student"
    )

    db.session.add(user)
    db.session.commit()

    student = Student(
        user_id=user.id
    )

    db.session.add(student)
    db.session.commit()

    return {"msg": "Student registered successfully"}


# UPDATE STUDENT PROFILE
@app.route('/student/profile', methods=['PUT'])
@jwt_required()
@role_required('student')
def update_profile():
    from models import Student
    from flask import request
    from app import db
    from flask_jwt_extended import get_jwt_identity

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    data = request.json

    student.branch = data.get('branch')
    student.cgpa = data.get('cgpa')
    student.graduation_year = data.get('graduation_year')
    student.skills = data.get('skills')
    student.resume_link = data.get('resume_link')

    db.session.commit()

    return {"msg": "Profile updated"}


# VIEW & SEARCH JOBS
@app.route('/student/jobs', methods=['GET'])
@jwt_required()
@role_required('student')
def view_jobs():
    from models import JobPosition, Company
    from flask import request

    search = request.args.get('search')

    query = JobPosition.query.join(Company).filter(
        JobPosition.is_active == True,
        JobPosition.is_approved == True
    )

    # Apply search ONLY if provided
    if search and search.strip() != "":
        query = query.filter(
            (JobPosition.title.ilike(f"%{search}%")) |
            (JobPosition.skills_required.ilike(f"%{search}%")) |
            (Company.company_name.ilike(f"%{search}%"))
        )

    jobs = query.all()

    return [{
        "id": j.id,
        "title": j.title,
        "company": j.company.company_name,
        "skills": j.skills_required,
        "salary": j.salary,
        "experience": j.experience
    } for j in jobs]

# APPLY FOR JOB
@app.route('/student/apply/<int:job_id>', methods=['POST'])
@jwt_required()
@role_required('student')
def apply_job(job_id):
    from models import Application, Student, JobPosition
    from app import db
    from flask_jwt_extended import get_jwt_identity

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    job = JobPosition.query.get(job_id)
    if not job or not job.is_active:
        return {"error": "Job not available"}, 404

    # Prevent duplicate apply
    existing = Application.query.filter_by(
        student_id=student.id,
        job_id=job_id
    ).first()

    if existing:
        return {"error": "Already applied"}, 400

    app_obj = Application(
        student_id=student.id,
        job_id=job_id
    )

    db.session.add(app_obj)
    db.session.commit()

    return {"msg": "Applied successfully"}

# VIEW MY APPLICATIONS
@app.route('/student/applications', methods=['GET'])
@jwt_required()
@role_required('student')
def my_applications():
    from models import Application, Student

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    apps = Application.query.filter_by(student_id=student.id).all()

    return [{
        "id": a.id,
        "job_title": a.job.title,
        "company": a.job.company.company_name,
        "status": a.status,
        "applied_date": str(a.applied_date),
        "interview_date": a.interview_date,
        "interview_location": a.interview_location,
        "feedback": a.feedback
    } for a in apps]

# VIEW INTERVIEWS
@app.route('/student/interviews', methods=['GET'])
@jwt_required()
@role_required('student')
def view_interviews():
    from models import Application, Student

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    interviews = Application.query.filter(
        Application.student_id == student.id,
        Application.interview_date != None
    ).all()

    return [{
        "job": a.job.title,
        "company": a.job.company.company_name,
        "date": a.interview_date,
        "location": a.interview_location
    } for a in interviews]

# VIEW PLACEMENTS
@app.route('/student/placements', methods=['GET'])
@jwt_required()
@role_required('student')
def view_placements():
    from models import Application, Student, Company, JobPosition

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    # We only want applications where the student was actually HIRED
    placements = Application.query.filter_by(
        student_id=student.id, 
        status='selected' # Make sure this matches your status name
    ).all()

    result = []
    for p in placements:
        # p is now an Application object
        job = JobPosition.query.get(p.job_id)
        # Get company via the job relationship
        company = Company.query.get(job.company_id) if job else None

        result.append({
            "application_id": p.id,
            "company": company.company_name if company else "N/A",
            "job_title": job.title if job else "N/A",
            "salary": p.salary,
            "joining_date": str(p.joining_date) if p.joining_date else "TBD",
            "offer_letter": p.offer_letter
        })

    return jsonify(result)

# DOWNLOAD OFFER LETTER
@app.route('/student/application/<int:id>/download', methods=['GET'])
@jwt_required()
@role_required('student')
def download_offer_letter(id):
    from models import Application, Student
    from flask import send_file

    user_id = get_jwt_identity()
    student = Student.query.filter_by(user_id=user_id).first()

    # Query the Application table instead
    application = Application.query.get(id)

    if not application or application.student_id != student.id:
        return {"error": "Unauthorized access"}, 403

    if not application.offer_letter:
        return {"error": "No offer letter has been uploaded yet"}, 404

    try:
        # application.offer_letter should be the file path on your server
        return send_file(application.offer_letter, as_attachment=True)
    except Exception as e:
        return {"error": f"Could not find file: {str(e)}"}, 404

if __name__ == "__main__":
    app.run(debug=True)
