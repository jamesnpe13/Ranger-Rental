from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.booking import Booking
from models.vehicle import Vehicle
from models.user import User
from datetime import datetime
from sqlalchemy import or_, and_

bp = Blueprint('bookings', __name__, url_prefix='/bookings')

def validate_booking_dates(start_date, end_date):
    """Validate booking dates."""
    try:
        start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
        
        if start >= end:
            return False, "End date must be after start date"
            
        if start < datetime.utcnow():
            return False, "Start date cannot be in the past"
            
        return True, (start, end)
    except (ValueError, TypeError) as e:
        return False, f"Invalid date format: {str(e)}. Use ISO format (e.g., 2025-06-01T10:00:00)"

@bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['vehicle_id', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'error': f'Missing required field: {field}'
            }), 400
    
    # Validate dates
    is_valid, date_result = validate_booking_dates(data['start_date'], data['end_date'])
    if not is_valid:
        return jsonify({
            'success': False,
            'error': date_result  # Contains the error message
        }), 400
    
    start_date, end_date = date_result
    
    # Check if vehicle exists
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({
            'success': False,
            'error': 'Vehicle not found'
        }), 404
    
    # Check if vehicle is available
    if not vehicle.is_available:
        return jsonify({
            'success': False,
            'error': 'Vehicle is not available for booking'
        }), 400
    
    # Check for booking conflicts
    if not Booking.is_vehicle_available(vehicle.id, start_date, end_date):
        return jsonify({
            'success': False,
            'error': 'Vehicle is already booked for the selected dates'
        }), 400
    
    # Calculate total price
    days = (end_date - start_date).days
    total_price = days * vehicle.price_per_day
    
    try:
        # Create booking
        booking = Booking(
            vehicle_id=vehicle.id,
            user_id=current_user_id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='confirmed'  # Could be 'pending' if payment is required first
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('', methods=['GET'])
@jwt_required()
def get_user_bookings():
    """Get all bookings for the current user."""
    current_user_id = get_jwt_identity()
    bookings = Booking.query.filter_by(user_id=current_user_id).all()
    
    return jsonify({
        'success': True,
        'bookings': [booking.to_dict() for booking in bookings]
    }), 200

@bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get a specific booking by ID."""
    current_user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the current user is the owner of the booking or an admin
    if booking.user_id != current_user_id and not User.query.get(current_user_id).is_admin:
        return jsonify({
            'success': False,
            'error': 'Unauthorized access to this booking'
        }), 403
    
    return jsonify({
        'success': True,
        'booking': booking.to_dict()
    }), 200

@bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    """Update a booking (cancel or change dates)."""
    current_user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if the current user is the owner of the booking
    if booking.user_id != current_user_id and not User.query.get(current_user_id).is_admin:
        return jsonify({
            'success': False,
            'error': 'Unauthorized to update this booking'
        }), 403
    
    data = request.get_json()
    
    # Only allow updating status and dates
    if 'status' in data and data['status'] in ['cancelled']:
        if booking.status == 'cancelled':
            return jsonify({
                'success': False,
                'error': 'Booking is already cancelled'
            }), 400
            
        booking.status = data['status']
        booking.updated_at = datetime.utcnow()
        
    # Handle date changes
    if 'start_date' in data or 'end_date' in data:
        start_date = data.get('start_date', booking.start_date.isoformat())
        end_date = data.get('end_date', booking.end_date.isoformat())
        
        is_valid, date_result = validate_booking_dates(start_date, end_date)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': date_result
            }), 400
            
        start_date, end_date = date_result
        
        # Check if the new dates are available
        if not Booking.is_vehicle_available(booking.vehicle_id, start_date, end_date, exclude_booking_id=booking.id):
            return jsonify({
                'success': False,
                'error': 'Vehicle is not available for the selected dates'
            }), 400
            
        # Update dates and recalculate price
        booking.start_date = start_date
        booking.end_date = end_date
        days = (end_date - start_date).days
        booking.total_price = days * booking.vehicle.price_per_day
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Booking updated successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    """Delete a booking (admin only)."""
    current_user = User.query.get(get_jwt_identity())
    
    if not current_user.is_admin:
        return jsonify({
            'success': False,
            'error': 'Admin access required'
        }), 403
    
    booking = Booking.query.get_or_404(booking_id)
    
    try:
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Booking deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
