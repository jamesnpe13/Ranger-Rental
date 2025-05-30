from flask import request, jsonify
from models import db, Vehicle
from . import bp
from auth.routes import admin_required
from functools import wraps

@bp.route('/vehicles', methods=['GET'])
def get_vehicles():
    # Get query parameters
    make = request.args.get('make')
    model = request.args.get('model')
    vehicle_type = request.args.get('type')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    available = request.args.get('available', 'true').lower() == 'true'

    # Build query
    query = Vehicle.query
    
    if make:
        query = query.filter(Vehicle.make.ilike(f'%{make}%'))
    if model:
        query = query.filter(Vehicle.model.ilike(f'%{model}%'))
    if vehicle_type:
        query = query.filter(Vehicle.type.ilike(f'%{vehicle_type}%'))
    if min_price:
        try:
            query = query.filter(Vehicle.price_per_day >= float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            query = query.filter(Vehicle.price_per_day <= float(max_price))
        except ValueError:
            pass
    if available:
        query = query.filter(Vehicle.is_available == True)

    # Execute query
    vehicles = query.all()
    return jsonify([vehicle.to_dict() for vehicle in vehicles])

@bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return jsonify(vehicle.to_dict())

@bp.route('/vehicles', methods=['POST'])
@admin_required
def create_vehicle():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['make', 'model', 'year', 'type', 'price_per_day']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new vehicle
    vehicle = Vehicle(
        make=data['make'],
        model=data['model'],
        year=data['year'],
        type=data['type'],
        price_per_day=data['price_per_day'],
        is_available=data.get('is_available', True),
        location=data.get('location'),
        description=data.get('description'),
        image_url=data.get('image_url')
    )
    
    db.session.add(vehicle)
    db.session.commit()
    
    return jsonify(vehicle.to_dict()), 201

@bp.route('/vehicles/<int:vehicle_id>', methods=['PUT'])
@admin_required
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    data = request.get_json()
    
    # Update fields if provided
    if 'make' in data:
        vehicle.make = data['make']
    if 'model' in data:
        vehicle.model = data['model']
    if 'year' in data:
        vehicle.year = data['year']
    if 'type' in data:
        vehicle.type = data['type']
    if 'price_per_day' in data:
        vehicle.price_per_day = data['price_per_day']
    if 'is_available' in data:
        vehicle.is_available = data['is_available']
    if 'location' in data:
        vehicle.location = data['location']
    if 'description' in data:
        vehicle.description = data['description']
    if 'image_url' in data:
        vehicle.image_url = data['image_url']
    
    db.session.commit()
    return jsonify(vehicle.to_dict())

@bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
@admin_required
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({'message': 'Vehicle deleted successfully'})
