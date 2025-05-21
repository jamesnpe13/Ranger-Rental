from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, Vehicle, Booking
from sqlalchemy import and_, or_
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('availability', __name__, url_prefix='/api/availability')

def validate_dates(start_date_str, end_date_str):
    """Validate and parse date strings"""
    try:
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        if start_date >= end_date:
            return None, None, ("End date must be after start date", 400)
            
        return start_date, end_date, None
    except (ValueError, AttributeError):
        return None, None, ("Invalid date format. Use ISO 8601 format (e.g., 2023-01-01T00:00:00Z)", 400)

@bp.route('/check', methods=['GET'])
def check_availability():
    """
    Check vehicle availability with filters
    ---
    parameters:
      - name: start_date
        in: query
        type: string
        format: date-time
        required: true
        description: Start date in ISO 8601 format (e.g., 2023-01-01T00:00:00Z)
      - name: end_date
        in: query
        type: string
        format: date-time
        required: true
        description: End date in ISO 8601 format (e.g., 2023-01-07T00:00:00Z)
      - name: make
        in: query
        type: string
      - name: type
        in: query
        type: string
      - name: min_price
        in: query
        type: number
      - name: max_price
        in: query
        type: number
    responses:
      200:
        description: List of available vehicles
      400:
        description: Invalid date range or format
    """
    # Parse and validate dates
    start_date, end_date, error = validate_dates(
        request.args.get('start_date'),
        request.args.get('end_date')
    )
    if error:
        return jsonify({"error": error[0]}), error[1]
    
    # Build base query
    query = Vehicle.query.filter_by(is_available=True)
    
    # Apply filters
    if 'make' in request.args:
        query = query.filter(Vehicle.make.ilike(f"%{request.args['make']}%"))
    if 'type' in request.args:
        query = query.filter(Vehicle.type.ilike(f"%{request.args['type']}%"))
    if 'min_price' in request.args:
        try:
            query = query.filter(Vehicle.price_per_day >= float(request.args['min_price']))
        except ValueError:
            pass
    if 'max_price' in request.args:
        try:
            query = query.filter(Vehicle.price_per_day <= float(request.args['max_price']))
        except ValueError:
            pass
    
    # Get all vehicles matching the filters
    vehicles = query.all()
    
    # Filter out vehicles with overlapping bookings
    available_vehicles = []
    for vehicle in vehicles:
        is_available = Booking.is_vehicle_available(vehicle.id, start_date, end_date)
        if is_available:
            available_vehicles.append(vehicle.to_dict())
    
    return jsonify(available_vehicles)

@bp.route('/vehicle/<int:vehicle_id>', methods=['GET'])
def check_vehicle_availability(vehicle_id):
    """
    Check availability for a specific vehicle
    ---
    parameters:
      - name: start_date
        in: query
        type: string
        format: date-time
        required: true
      - name: end_date
        in: query
        type: string
        format: date-time
        required: true
    responses:
      200:
        description: Availability status for the vehicle
      400:
        description: Invalid date range or format
      404:
        description: Vehicle not found
    """
    # Parse and validate dates
    start_date, end_date, error = validate_dates(
        request.args.get('start_date'),
        request.args.get('end_date')
    )
    if error:
        return jsonify({"error": error[0]}), error[1]
    
    # Check if vehicle exists
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    # Check availability
    is_available = Booking.is_vehicle_available(vehicle_id, start_date, end_date)
    
    return jsonify({
        'vehicle_id': vehicle_id,
        'is_available': is_available,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    })

@bp.route('/book', methods=['POST'])
@jwt_required()
def book_vehicle():
    """
    Book a vehicle
    ---
    parameters:
      - in: body
        name: booking
        required: true
        schema:
          type: object
          required:
            - vehicle_id
            - start_date
            - end_date
          properties:
            vehicle_id:
              type: integer
            start_date:
              type: string
              format: date-time
            end_date:
              type: string
              format: date-time
    responses:
      201:
        description: Booking created successfully
      400:
        description: Invalid input or vehicle not available
      404:
        description: Vehicle not found
    """
    data = request.get_json()
    
    # Validate required fields
    if not all(key in data for key in ['vehicle_id', 'start_date', 'end_date']):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Parse and validate dates
    start_date, end_date, error = validate_dates(
        data['start_date'],
        data['end_date']
    )
    if error:
        return jsonify({"error": error[0]}), error[1]
    
    # Check if vehicle exists and is available
    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    if not vehicle.is_available:
        return jsonify({"error": "Vehicle is not available for booking"}), 400
    
    # Check availability
    is_available = Booking.is_vehicle_available(vehicle.id, start_date, end_date)
    if not is_available:
        return jsonify({"error": "Vehicle is not available for the selected dates"}), 400
    
    # Create booking
    try:
        booking = Booking(
            vehicle_id=vehicle.id,
            user_id=get_jwt_identity(),
            start_date=start_date,
            end_date=end_date,
            status='confirmed'
        )
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            "message": "Booking created successfully",
            "booking_id": booking.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
