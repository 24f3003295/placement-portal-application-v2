from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
