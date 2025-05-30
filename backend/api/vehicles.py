"""
Vehicle-related API endpoints.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..core import db
from ..models import Vehicle, User, Booking
from ..schemas import VehicleSchema
from ..services import VehicleService
from ..utils import admin_required, validate_dates

# Create blueprint
vehicles_bp = Blueprint('vehicles', __name__)
vehicle_schema = VehicleSchema()

@vehicles_bp.route('', methods=['GET'])
def get_vehicles():
    """Get all available vehicles with optional filters."""
    # Get query parameters
    vehicle_type = request.args.get('type')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    location = request.args.get('location')
    
    # Start building the query
    query = Vehicle.query.filter_by(is_available=True)
    
    # Apply filters
    if vehicle_type:
        query = query.filter(Vehicle.type == vehicle_type)
    if min_price is not None:
        query = query.filter(Vehicle.price_per_day >= min_price)
    if max_price is not None:
        query = query.filter(Vehicle.price_per_day <= max_price)
    if location:
        query = query.filter(Vehicle.location.ilike(f'%{location}%'))
    
    # Execute query
    vehicles = query.all()
    
    return jsonify([{
        'id': v.id,
        'make': v.make,
        'model': v.model,
        'year': v.year,
        'type': v.type,
        'price_per_day': float(v.price_per_day),
        'location': v.location,
        'description': v.description,
        'image_urls': v.image_urls or []
    } for v in vehicles])

@vehicles_bp.route('/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    """Get details of a specific vehicle."""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check availability
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        is_available = vehicle.check_availability(start_date, end_date)
    else:
        is_available = vehicle.is_available
    
    return jsonify({
        **vehicle.to_dict(),
        'is_available': is_available
    })

@vehicles_bp.route('', methods=['POST'])
@jwt_required()
def create_vehicle():
    """Create a new vehicle (for vehicle owners/admins)."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    errors = vehicle_schema.validate(data)
    if errors:
        return jsonify({"error": "Validation error", "details": errors}), 400
    
    try:
        # Create new vehicle
        vehicle = VehicleService.create_vehicle(data, user_id)
        return jsonify(vehicle.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@vehicles_bp.route('/<int:vehicle_id>/availability', methods=['GET'])
def check_availability(vehicle_id):
    """Check vehicle availability for given dates."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"error": "Both start_date and end_date are required"}), 400
    
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Validate dates
    is_valid, result = validate_dates(start_date, end_date)
    if not is_valid:
        return jsonify(result), 400
    
    # Check availability
    is_available = vehicle.check_availability(result['start_date'], result['end_date'])
    
    return jsonify({
        'vehicle_id': vehicle.id,
        'is_available': is_available,
        'start_date': result['start_date'].isoformat(),
        'end_date': result['end_date'].isoformat()
    })

@vehicles_bp.route('/<int:vehicle_id>', methods=['PUT'])
@jwt_required()
def update_vehicle(vehicle_id):
    """Update vehicle details (owner or admin only)."""
    user_id = get_jwt_identity()
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check permissions
    user = User.query.get(user_id)
    if not user.is_admin and vehicle.owner_id != user_id:
        return jsonify({"error": "Not authorized to update this vehicle"}), 403
    
    data = request.get_json()
    
    # Update fields
    for field in ['make', 'model', 'year', 'type', 'price_per_day', 'location', 'description', 'is_available']:
        if field in data:
            setattr(vehicle, field, data[field])
    
    try:
        db.session.commit()
        return jsonify(vehicle.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@vehicles_bp.route('/<int:vehicle_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_vehicle(vehicle_id):
    """Delete a vehicle (admin only)."""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    try:
        db.session.delete(vehicle)
        db.session.commit()
        return jsonify({"message": "Vehicle deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
