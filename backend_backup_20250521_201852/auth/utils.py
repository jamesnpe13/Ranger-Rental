from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    verify_jwt_in_request,
    get_jwt
)
from models import User, db
from datetime import timedelta

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def create_auth_token(user):
    """Create JWT token for authenticated user"""
    additional_claims = {
        'role': user.role,
        'username': user.username,
        'email': user.email
    }
    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims,
        expires_delta=timedelta(days=1)
    )
    return access_token

def register_user(username, email, password, role='customer'):
    """Register a new user"""
    if User.query.filter_by(username=username).first():
        return None, 'Username already exists'
    if User.query.filter_by(email=email).first():
        return None, 'Email already registered'
    
    try:
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)

def authenticate_user(username, password):
    """Authenticate user and return user object if successful"""
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return None, 'Invalid username or password'
    if not user.is_active:
        return None, 'Account is deactivated'
    return user, None

def get_current_user():
    """Get the current authenticated user"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)