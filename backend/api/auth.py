from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request
)
from werkzeug.security import check_password_hash, generate_password_hash
from models import db
from models.user import User

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def admin_required(fn):
    """Decorator to require admin privileges."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
            
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens."""
    print("\n=== New Login Attempt ===")
    print(f"Request headers: {request.headers}")
    print(f"Request content type: {request.content_type}")
    
    try:
        data = request.get_json()
        print(f"Received data: {data}")
    except Exception as e:
        print(f"Error parsing JSON: {str(e)}")
        return jsonify({"error": "Invalid JSON data"}), 400
        
    if not data:
        print("No data received in request")
        return jsonify({"error": "No input data provided"}), 400

    email = data.get('email') or data.get('username')  # Try both 'email' and 'username' fields
    password = data.get('password')
    
    print(f"Extracted - Email/Username: {email}, Password: {'*' * len(password) if password else 'None'}")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    print(f"Attempting login for: {email}")
    
    # Try to find user by email first, then by username
    user = User.query.filter((User.email == email) | (User.username == email)).first()
    
    if not user:
        print(f"No user found with email/username: {email}")
        return jsonify({"error": "Invalid username/email or password"}), 401
        
    print(f"User found: {user.username}")
    print(f"Stored password hash: {user.password}")
    
    # Debug: Check password directly
    is_password_correct = user.check_password(password)
    print(f"Password check result: {is_password_correct}")
    
    if not is_password_correct:
        return jsonify({"error": "Invalid email or password"}), 401

    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "message": "Login successful"
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    # Only allow admin to create admin users
    if is_admin:
        # Check if user is authenticated and is admin
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            if not current_user or not current_user.is_admin:
                return jsonify({"error": "Admin privileges required to create admin users"}), 403
        except:
            return jsonify({"error": "Admin privileges required to create admin users"}), 403

    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 400

    # Create user with password in constructor
    new_user = User(
        username=username,
        email=email,
        password=password,  # Pass password to constructor
        is_admin=is_admin
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Create tokens for the new user
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        
        return jsonify({
            "message": "User registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "is_admin": new_user.is_admin
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_token})

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all users (admin only)."""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200
