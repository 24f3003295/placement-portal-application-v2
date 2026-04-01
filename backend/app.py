from flask import Flask
from models import db, User
from auth import auth_bp
from utils import role_required
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash


app = Flask(__name__)
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

if __name__ == "__main__":
    app.run(debug=True)