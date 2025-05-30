from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
    create_refresh_token,
    jwt_required,
    verify_jwt_in_request
)
from models import User, db
from . import jwt
from functools import wraps

# Create a Blueprint for auth routes
bp = Blueprint('auth', __name__)

def admin_required(fn):
    """Decorator to require admin role"""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if not current_user or current_user.role != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return decorated_function

def register_user(username, email, password, role='customer'):
    """Register a new user"""
    if User.query.filter_by(username=username).first():
        return None, 'Username already exists'
    if User.query.filter_by(email=email).first():
        return None, 'Email already registered'
    
    user = User(username=username, email=email, password=password, role=role)
    db.session.add(user)
    db.session.commit()
    return user, None

def authenticate_user(email, password):
    """Authenticate a user by email and password"""
    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return None, 'Invalid email or password'
    if not user.is_active:
        return None, 'Account is deactivated'
    return user, None

def create_auth_token(user):
    """Create JWT token for the user"""
    return create_access_token(identity=user)

def get_current_user():
    """Get the current user from JWT token"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              minLength: 3
              maxLength: 50
            email:
              type: string
              format: email
            password:
              type: string
              minLength: 8
            role:
              type: string
              enum: [customer, admin]
              default: customer
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid input
    """
    data = request.get_json()
    
    # Input validation
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Basic email validation
    if '@' not in data['email']:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Password strength check
    if len(data['password']) < 8:
        return jsonify({
            'error': 'Password must be at least 8 characters long',
            'code': 'PASSWORD_TOO_SHORT'
        }), 400

    # Register user (default to 'customer' role unless specified)
    user, error = register_user(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data.get('role', 'customer')
    )
    
    if error:
        return jsonify({'error': error, 'code': 'REGISTRATION_FAILED'}), 400
    
    # Generate JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    """
    User login with direct User model authentication
    """
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    try:
        # Get user using the User model
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"No user found with email: {email}")
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password using the User model's method
        if not user.verify_password(password):
            print(f"Password verification failed for user: {email}")
            return jsonify({"error": "Invalid email or password"}), 401
            
        if not user.is_active:
            print(f"Account is deactivated for user: {email}")
            return jsonify({"error": "Account is deactivated"}), 401
            
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Prepare user data for response
        user_response = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }
        
        print(f"Successful login for user: {email}")
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user_response
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An error occurred during login"}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - auth
    security:
      - Bearer: []
    responses:
      200:
        description: Token refreshed
      401:
        description: Invalid or expired refresh token
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=access_token)

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """
    Get current user's profile
    ---
    tags:
      - users
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    """
    Update current user's profile
    ---
    tags:
      - users
    security:
      - Bearer: []
    parameters:
      - in: body
        name: user_data
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
            password:
              type: string
              minLength: 8
    responses:
      200:
        description: User updated successfully
      400:
        description: Invalid input
      401:
        description: Unauthorized
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    data = request.get_json()
    
    if 'email' in data:
        if User.query.filter(User.email == data['email'], User.id != current_user_id).first():
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    
    if 'password' in data and data['password']:
        if len(data['password']) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully', 'user': user.to_dict()})

@bp.route('/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    """
    List all users (admin only)
    ---
    tags:
      - admin
    security:
      - Bearer: []
    responses:
      200:
        description: List of users
      403:
        description: Admin access required
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@bp.route('/admin/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """
    Get user by ID (admin only)
    ---
    tags:
      - admin
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: User details
      403:
        description: Admin access required
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """
    Update user by ID (admin only)
    ---
    tags:
      - admin
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: body
        name: user_data
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
            role:
              type: string
              enum: [admin, customer]
            is_active:
              type: boolean
    security:
      - Bearer: []
    responses:
      200:
        description: User updated successfully
      400:
        description: Invalid input
      403:
        description: Admin access required
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'email' in data and data['email'] != user.email:
        if User.query.filter(User.email == data['email']).first():
            return jsonify({'error': 'Email already in use'}), 400
        user.email = data['email']
    
    if 'role' in data and data['role'] in ['admin', 'customer']:
        user.role = data['role']
    
    if 'is_active' in data and isinstance(data['is_active'], bool):
        user.is_active = data['is_active']
    
    db.session.commit()
    return jsonify({'message': 'User updated successfully', 'user': user.to_dict()})

@bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """
    Delete user by ID (admin only)
    ---
    tags:
      - admin
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: User deleted successfully
      403:
        description: Admin access required
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Prevent deleting yourself
    current_user_id = get_jwt_identity()
    if user.id == current_user_id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})