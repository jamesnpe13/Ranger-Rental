from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..models.user import User

def admin_required(fn):
    """Decorator to ensure the user has admin privileges."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({"error": "Administrator access required"}), 403
            
        return fn(*args, **kwargs)
    return wrapper
