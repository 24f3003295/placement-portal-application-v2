from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# USER 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20))  # admin, company, student
    is_active = db.Column(db.Boolean, default=True)

    student = db.relationship('Student', backref='user', uselist=False)


# COMPANY 
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(150))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default='pending')
    is_blacklisted = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='company', uselist=False)

    jobs = db.relationship('JobPosition', backref='company', lazy=True)


# STUDENT
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    graduation_year = db.Column(db.Integer)
    skills = db.Column(db.Text)
    resume_link = db.Column(db.String(200))
    is_blacklisted = db.Column(db.Boolean, default=False)

    applications = db.relationship('Application', backref='student', lazy=True)
    placements = db.relationship('Placement', backref='student', lazy=True)


# JOB POSITION 
class JobPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    salary = db.Column(db.Float)
    skills_required = db.Column(db.Text)
    experience = db.Column(db.String(50))
    eligibility_criteria = db.Column(db.String(200))
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    is_approved = db.Column(db.Boolean, default=False)


    applications = db.relationship('Application', backref='job', lazy=True)


# APPLICATION
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job_position.id'))
    status = db.Column(db.String(20), default='applied')
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.String(255))
    interview_date = db.Column(db.String(50))
    interview_location = db.Column(db.String(255))

    placement = db.relationship('Placement', backref='application', uselist=False)


# PLACEMENT 
class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey('application.id'),
        unique=True
    )

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job_position.id'))

    salary = db.Column(db.Float)
    joining_date = db.Column(db.Date)
