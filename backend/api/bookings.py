"""
Booking-related API endpoints.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..core import db
from ..models import Booking, Vehicle, User
from ..schemas import BookingSchema
from ..services import BookingService
from ..utils import admin_required, validate_dates, calculate_total_price

# Create blueprint
bookings_bp = Blueprint('bookings', __name__)
booking_schema = BookingSchema()

@bookings_bp.route('', methods=['GET'])
@jwt_required()
def get_user_bookings():
    """Get all bookings for the current user."""
    user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': b.id,
        'vehicle_id': b.vehicle_id,
        'start_date': b.start_date.isoformat(),
        'end_date': b.end_date.isoformat(),
        'total_price': float(b.total_price) if b.total_price else None,
        'status': b.status,
        'created_at': b.created_at.isoformat(),
        'vehicle': {
            'make': b.vehicle.make,
            'model': b.vehicle.model,
            'image_url': b.vehicle.image_urls[0] if b.vehicle.image_urls else None
        } if b.vehicle else None
    } for b in bookings])

@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get details of a specific booking."""
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    # Check permissions
    user = User.query.get(user_id)
    if not user.is_admin and booking.user_id != user_id:
        return jsonify({"error": "Not authorized to view this booking"}), 403
    
    return jsonify(booking.to_dict(include_vehicle=True, include_user=user.is_admin))

@bookings_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vehicle_id', 'start_date', 'end_date']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Validate dates
    is_valid, result = validate_dates(data['start_date'], data['end_date'])
    if not is_valid:
        return jsonify(result), 400
    
    # Check if vehicle exists and is available
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    if not vehicle.is_available:
        return jsonify({"error": "Vehicle is not available for booking"}), 400
    
    # Check if vehicle is available for the selected dates
    if not vehicle.check_availability(result['start_date'], result['end_date']):
        return jsonify({"error": "Vehicle is not available for the selected dates"}), 400
    
    try:
        # Calculate total price
        days = (result['end_date'] - result['start_date']).days + 1
        total_price = vehicle.price_per_day * days
        
        # Create booking
        booking = Booking(
            vehicle_id=vehicle.id,
            user_id=user_id,
            start_date=result['start_date'],
            end_date=result['end_date'],
            total_price=total_price,
            status='confirmed'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict(include_vehicle=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bookings_bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """Update a booking (only status updates are allowed)."""
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    # Check permissions
    user = User.query.get(user_id)
    if not user.is_admin and booking.user_id != user_id:
        return jsonify({"error": "Not authorized to update this booking"}), 403
    
    data = request.get_json()
    
    # Only allow status updates for non-admins
    if 'status' in data and not user.is_admin:
        return jsonify({"error": "Only admins can update booking status"}), 403
    
    # Update status if provided
    if 'status' in data:
        booking.status = data['status']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Booking updated successfully',
            'booking': booking.to_dict(include_vehicle=True)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bookings_bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def cancel_booking(booking_id):
    """Cancel a booking."""
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    # Check permissions
    user = User.query.get(user_id)
    if not user.is_admin and booking.user_id != user_id:
        return jsonify({"error": "Not authorized to cancel this booking"}), 403
    
    # Only allow cancelling pending or confirmed bookings
    if booking.status not in ['pending', 'confirmed']:
        return jsonify({"error": f"Cannot cancel a {booking.status} booking"}), 400
    
    try:
        # Update status to cancelled
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'booking_id': booking_id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
