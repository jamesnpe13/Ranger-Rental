from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
from models.vehicle import Vehicle
from models.user import User
from models import db

bp = Blueprint('vehicles', __name__, url_prefix='/api/vehicles')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('', methods=['GET'])
@login_required
@admin_required
def get_vehicles():
    try:
        # Get query parameters
        available = request.args.get('available', type=str)
        make = request.args.get('make')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        # Start building the query
        query = Vehicle.query
        
        # Apply filters
        if available is not None:
            query = query.filter(Vehicle.is_available == (available.lower() == 'true'))
        if make:
            query = query.filter(Vehicle.make.ilike(f'%{make}%'))
        if min_price is not None:
            query = query.filter(Vehicle.price_per_day >= min_price)
        if max_price is not None:
            query = query.filter(Vehicle.price_per_day <= max_price)
            
        # Execute query and format response
        vehicles = query.order_by(Vehicle.id.desc()).all()
        return jsonify({
            'success': True,
            'vehicles': [{
                'id': v.id,
                'make': v.make,
                'model': v.model,
                'year': v.year,
                'type': v.type,
                'price_per_day': v.price_per_day,
                'is_available': v.is_available,
                'location': v.location,
                'description': v.description,
                'image_url': v.image_url,
                'owner_id': v.owner_id
            } for v in vehicles]
        })
    except Exception as e:
        current_app.logger.error(f'Error fetching vehicles: {str(e)}')
        return jsonify({'success': False, 'error': 'Failed to fetch vehicles'}), 500

@bp.route('', methods=['POST'])
@login_required
@admin_required
def create_vehicle():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['make', 'model', 'year', 'type', 'price_per_day', 'owner_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields. Required: make, model, year, type, price_per_day, owner_id'
            }), 400
            
        # Check if owner exists
        owner = User.query.get(data['owner_id'])
        if not owner:
            return jsonify({
                'success': False,
                'error': 'Owner not found'
            }), 404
            
        # Create new vehicle
        vehicle = Vehicle(
            make=data['make'],
            model=data['model'],
            year=data['year'],
            type=data['type'],
            price_per_day=float(data['price_per_day']),
            is_available=data.get('is_available', True),
            location=data.get('location', ''),
            description=data.get('description', ''),
            image_url=data.get('image_url', ''),
            owner_id=data['owner_id']
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle created successfully',
            'vehicle': vehicle.to_dict()
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Invalid data format: ' + str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating vehicle: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to create vehicle'
        }), 500

@bp.route('/<int:vehicle_id>', methods=['GET'])
@login_required
@admin_required
def get_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        return jsonify({
            'success': True,
            'vehicle': vehicle.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f'Error fetching vehicle {vehicle_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to fetch vehicle details'
        }), 500

@bp.route('/<int:vehicle_id>', methods=['PUT'])
@login_required
@admin_required
def update_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        # Update fields if they exist in the request
        if 'make' in data:
            vehicle.make = data['make']
        if 'model' in data:
            vehicle.model = data['model']
        if 'year' in data:
            vehicle.year = data['year']
        if 'type' in data:
            vehicle.type = data['type']
        if 'price_per_day' in data:
            vehicle.price_per_day = float(data['price_per_day'])
        if 'is_available' in data:
            vehicle.is_available = bool(data['is_available'])
        if 'location' in data:
            vehicle.location = data['location']
        if 'description' in data:
            vehicle.description = data['description']
        if 'image_url' in data:
            vehicle.image_url = data['image_url']
        if 'owner_id' in data:
            # Verify new owner exists
            if not User.query.get(data['owner_id']):
                return jsonify({
                    'success': False,
                    'error': 'Owner not found'
                }), 404
            vehicle.owner_id = data['owner_id']
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle.to_dict()
        })
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Invalid data format: ' + str(e)
        }), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating vehicle {vehicle_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to update vehicle'
        }), 500

@bp.route('/<int:vehicle_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Check for active bookings
        from models.booking import Booking
        active_bookings = Booking.query.filter(
            Booking.vehicle_id == vehicle_id,
            Booking.status.in_(['pending', 'confirmed', 'active'])
        ).count()
        
        if active_bookings > 0:
            return jsonify({
                'success': False,
                'error': 'Cannot delete vehicle with active bookings'
            }), 400
            
        # Delete the vehicle
        db.session.delete(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Vehicle deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting vehicle {vehicle_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to delete vehicle'
        }), 500
