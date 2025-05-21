from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User
from functools import wraps

# Using a unique name and URL prefix to avoid conflicts
bp = Blueprint('admin_api', __name__, url_prefix='/api/v1/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        if not current_user or current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Admin access required',
                    'status': 403
                }
            }), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()
    return jsonify({
        'success': True,
        'data': [{
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active
        } for user in users]
    })

@bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required
def update_user_role(user_id):
    data = request.get_json()
    if not data or 'role' not in data:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_INPUT',
                'message': 'Role is required',
                'status': 400
            }
        }), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'User not found',
                'status': 404
            }
        }), 404
    
    user.role = data['role']
    db.session.commit()
    
    return jsonify({
        'success': True,
        'data': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active
        }
    })
