"""
Admin-only API endpoints.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..core import db
from ..models import User, Vehicle, Booking
from ..schemas import UserSchema, VehicleSchema, BookingSchema
from ..utils import admin_required

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
user_schema = UserSchema()
vehicle_schema = VehicleSchema()
booking_schema = BookingSchema()

# Users Management
@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all users (admin only)."""
    users = User.query.all()
    return jsonify([user_schema.dump(user) for user in users])

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user(user_id):
    """Get user by ID (admin only)."""
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user))

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user (admin only)."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Update fields
    for field in ['email', 'first_name', 'last_name', 'role', 'is_active']:
        if field in data:
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        return jsonify(user_schema.dump(user))
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Vehicles Management
@admin_bp.route('/vehicles', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_vehicles():
    """Get all vehicles (admin only)."""
    vehicles = Vehicle.query.all()
    return jsonify([{
        **vehicle.to_dict(),
        'owner': {
            'id': vehicle.owner.id,
            'email': vehicle.owner.email,
            'name': f"{vehicle.owner.first_name} {vehicle.owner.last_name}"
        } if vehicle.owner else None
    } for vehicle in vehicles])

# Bookings Management
@admin_bp.route('/bookings', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_bookings():
    """Get all bookings (admin only)."""
    status = request.args.get('status')
    
    query = Booking.query
    if status:
        query = query.filter_by(status=status)
    
    bookings = query.all()
    
    return jsonify([{
        'id': b.id,
        'start_date': b.start_date.isoformat(),
        'end_date': b.end_date.isoformat(),
        'total_price': float(b.total_price) if b.total_price else None,
        'status': b.status,
        'created_at': b.created_at.isoformat(),
        'user': {
            'id': b.user.id,
            'email': b.user.email,
            'name': f"{b.user.first_name} {b.user.last_name}"
        },
        'vehicle': {
            'id': b.vehicle.id,
            'make': b.vehicle.make,
            'model': b.vehicle.model,
            'year': b.vehicle.year
        } if b.vehicle else None
    } for b in bookings])

# System Stats
@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_system_stats():
    """Get system statistics (admin only)."""
    stats = {
        'total_users': User.query.count(),
        'total_vehicles': Vehicle.query.count(),
        'total_bookings': Booking.query.count(),
        'active_bookings': Booking.query.filter_by(status='confirmed').count(),
        'available_vehicles': Vehicle.query.filter_by(is_available=True).count(),
        'revenue': float(db.session.query(db.func.sum(Booking.total_price))
                      .filter(Booking.status == 'confirmed').scalar() or 0)
    }
    
    return jsonify(stats)
