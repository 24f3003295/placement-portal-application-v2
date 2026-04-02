from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps
from flask import jsonify
from models import User   

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()

            # Fetch user from DB
            user = User.query.get(int(user_id))

            if not user or user.role != role:
                return jsonify({"error": "Unauthorized"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper
