from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.vehicle import Vehicle
from models.user import User
from datetime import datetime

bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

@bp.route('', methods=['GET'])
def get_vehicles():
    """Get all vehicles"""
    vehicles = Vehicle.query.all()
    return jsonify({
        'success': True,
        'vehicles': [vehicle.to_dict() for vehicle in vehicles]
    }), 200

@bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Get a specific vehicle by ID"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify({
        'success': True,
        'vehicle': vehicle.to_dict()
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_vehicle():
    """Create a new vehicle (admin only)"""
    print("=== CREATE VEHICLE REQUEST STARTED ===")
    print(f"Request data: {request.get_json()}")
    
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.get_json()
    print(f"Parsed JSON data: {data}")
    
    required_fields = ['make', 'model', 'year', 'type', 'price_per_day']
    
    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400
    
    try:
        # Handle image_url and image_urls (support both for backward compatibility)
        image_url = data.get('image_url') or data.get('image_urls')
        print(f"Using image_url: {image_url}")
        
        # Create a clean data dictionary with only valid Vehicle attributes
        vehicle_data = {
            'make': data['make'],
            'model': data['model'],
            'year': data['year'],
            'type': data['type'],
            'price_per_day': data['price_per_day'],
            'location': data.get('location'),
            'description': data.get('description'),
            'image_url': image_url,
            'owner_id': current_user_id,
            'is_available': data.get('is_available', True)
        }
        
        print(f"Vehicle data to create: {vehicle_data}")
        
        # Create vehicle with explicit parameters
        vehicle = Vehicle(**vehicle_data)
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle created successfully',
            'vehicle': vehicle.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    """Update a vehicle (admin only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    
    try:
        # Update fields if they exist in the request
        for field in ['make', 'model', 'year', 'type', 'price_per_day', 
                     'location', 'description', 'is_available']:
            if field in data:
                setattr(vehicle, field, data[field])
        
        # Handle image_url and image_urls (support both for backward compatibility)
        if 'image_url' in data or 'image_urls' in data:
            vehicle.image_url = data.get('image_url') or data.get('image_urls')
        
        vehicle.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
def delete_vehicle(vehicle_id):
    """Delete a vehicle (admin only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    try:
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/available', methods=['GET'])
def get_available_vehicles():
    """Get vehicles available for specific dates"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({
            'success': False,
            'error': 'Both start_date and end_date are required'
        }), 400
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Get all available vehicles
        available_vehicles = []
        vehicles = Vehicle.query.filter_by(is_available=True).all()
        
        for vehicle in vehicles:
            if vehicle.is_available_for_dates(start, end):
                available_vehicles.append(vehicle)
        
        return jsonify({
            'success': True,
            'vehicles': [v.to_dict() for v in available_vehicles],
            'count': len(available_vehicles)
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid date format. Use ISO format (e.g., 2025-06-01T10:00:00)'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
