from flask import Blueprint, request, jsonify
from models import db, User, Student,Company
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash,check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.json

    user = User(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role='student'
    )

    db.session.add(user)
    db.session.flush()  # get user.id

    student = Student(
        user_id=user.id,
        branch=data.get('branch'),
        cgpa=data.get('cgpa')
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"})



@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.json

    user = User(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role='company'
    )

    db.session.add(user)
    db.session.flush()

    company = Company(
        user_id=user.id,
        company_name=data['company_name'],
        approval_status='pending'
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({"message": "Company registered, waiting for admin approval"})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    if user.role == 'company':
        company = Company.query.filter_by(user_id=user.id).first()
        
        if not company:
            return jsonify({"error": "Company profile missing"}), 404

        if company.approval_status != 'approved':
            return jsonify({"error": "Company not approved by admin"}), 403

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "token": token,
        "role": user.role
    })

