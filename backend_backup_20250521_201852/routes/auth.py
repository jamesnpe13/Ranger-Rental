from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, Unauthorized, Conflict
from email_validator import validate_email, EmailNotValidError
from datetime import timedelta

from models.user import User, db, bcrypt

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_user_data(data, is_update=False):
    required_fields = ['email', 'password', 'first_name', 'last_name']
    if not is_update:
        required_fields.append('password')
    
    if not data or not all(field in data for field in required_fields):
        raise BadRequest('Missing required fields')
    
    try:
        # Validate email
        email = validate_email(data['email']).email
        data['email'] = email
    except EmailNotValidError as e:
        raise BadRequest('Invalid email address')
    
    # Validate password strength
    if not is_update or 'password' in data:
        if len(data['password']) < 8:
            raise BadRequest('Password must be at least 8 characters long')
    
    return data

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    try:
        data = validate_user_data(data)
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            raise Conflict('Email already registered')
        
        # Create new user
        user = User(
            email=data['email'],
            password=data['password'],  # This will be hashed by the User model
            first_name=data['first_name'],
            last_name=data['last_name'],
            role='customer'  # Default role
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate access token
        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Conflict as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred during registration"}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    try:
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.verify_password(data['password']):
            raise Unauthorized('Invalid email or password')
        
        if not user.is_active:
            raise Unauthorized('Account is deactivated')
        
        # Create access token that expires in 1 day
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role},
            expires_delta=timedelta(days=1)
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        })
        
    except Unauthorized as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "An error occurred during login"}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify(user.to_dict())

@bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Only allow users to update their own profile unless they're admin
    if current_user_id != user_id and current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if 'email' in data and data['email'] != user.email:
            if User.query.filter(User.email == data['email'], User.id != user.id).first():
                raise Conflict('Email already in use')
        
        # Update user fields
        for field in ['first_name', 'last_name', 'email']:
            if field in data:
                setattr(user, field, data[field])
        
        # Only allow admins to change roles
        if 'role' in data and current_user.role == 'admin':
            user.role = data['role']
            
        # Update password if provided
        if 'password' in data and data['password']:
            user.password = data['password']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Conflict as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating user"}), 500
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (data['username'],))
        user = cursor.fetchone()
        
        if user is None or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({"error": "Invalid username or password"}), 401
        
        return jsonify({
            "message": "Login successful",
            "user_id": user['id'],
            "username": user['username'],
            "role": user['role']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
