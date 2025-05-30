"""
Authentication and authorization routes.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User
from schemas.user_schema import UserSchema
from utils.decorators import admin_required

# Create blueprint
auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    # Validate input
    errors = user_schema.validate(data)
    if errors:
        return jsonify({"error": "Validation error", "details": errors}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400
    
    try:
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        user.password = data['password']
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "user": user_schema.dump(user),
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_schema.dump(user)
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_token})

@auth_bp.route('/me')
@jwt_required()
def get_current_user():
    """Get current user's profile."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user))

@auth_bp.route('/admin/users')
@jwt_required()
@admin_required
def get_all_users():
    """Get all users (admin only)."""
    users = User.query.all()
    return jsonify([user_schema.dump(user) for user in users])
