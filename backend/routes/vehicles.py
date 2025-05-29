import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from werkzeug.utils import secure_filename
from models.vehicle import Vehicle
from models.user import User
from models.booking import Booking
from models import db
from datetime import datetime
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename
import os

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bp = Blueprint('vehicles', __name__, url_prefix='/api/vehicles')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('', methods=['GET'])
def get_vehicles():
    """
    Get all vehicles with optional filtering
    Query params:
    - search: Search in make, model, or description
    - make: Filter by make
    - model: Filter by model
    - type: Filter by vehicle type
    - min_price/max_price: Filter by price range
    - available: Filter by availability (true/false)
    """
    try:
        # Get query parameters
        available = request.args.get('available')
        make = request.args.get('make')
        model = request.args.get('model')
        vehicle_type = request.args.get('type')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        search = request.args.get('search')
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Start building the query
        query = Vehicle.query
        
        # Apply filters
        if available is not None:
            query = query.filter(Vehicle.is_available == (available.lower() == 'true'))
        if make:
            query = query.filter(Vehicle.make.ilike(f'%{make}%'))
        if model:
            query = query.filter(Vehicle.model.ilike(f'%{model}%'))
        if vehicle_type:
            query = query.filter(Vehicle.type.ilike(f'%{vehicle_type}%'))
        if min_price is not None:
            query = query.filter(Vehicle.price_per_day >= min_price)
        if max_price is not None:
            query = query.filter(Vehicle.price_per_day <= max_price)
        if search:
            search = f'%{search}%'
            query = query.filter(
                (Vehicle.make.ilike(search)) |
                (Vehicle.model.ilike(search)) |
                (Vehicle.description.ilike(search))
            )
            
        # Execute query with pagination
        vehicles = query.order_by(Vehicle.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False)
            
        return jsonify({
            'success': True,
            'total': vehicles.total,
            'pages': vehicles.pages,
            'current_page': vehicles.page,
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
                'image_urls': v.image_urls or [],
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
def get_vehicle(vehicle_id):
    """Get details of a specific vehicle"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        return jsonify({
            'success': True,
            'vehicle': vehicle.to_dict(include_owner=True)
        })
    except Exception as e:
        current_app.logger.error(f'Error fetching vehicle {vehicle_id}: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to fetch vehicle details'
        }), 500

@bp.route('/<int:vehicle_id>/availability', methods=['GET'])
def check_vehicle_availability(vehicle_id):
    """
    Check if a vehicle is available for the given date range
    Query params:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'start_date and end_date are required'}), 400
            
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if start_date >= end_date:
            return jsonify({'error': 'end_date must be after start_date'}), 400
            
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        is_available = vehicle.check_availability(start_date, end_date)
        
        return jsonify({
            'success': True,
            'available': is_available,
            'vehicle_id': vehicle_id,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'vehicle': vehicle.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        current_app.logger.error(f'Error checking availability: {str(e)}')
        return jsonify({'error': 'Failed to check availability'}), 500

@bp.route('/<int:vehicle_id>/images', methods=['POST'])
@login_required
@admin_required
def upload_vehicle_image(vehicle_id):
    """
    Upload an image for a vehicle
    Requires admin privileges
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return jsonify({'error': 'Invalid file type. Only PNG, JPG, and GIF are allowed.'}), 400
            
        # Secure the filename and save
        filename = f'vehicle_{vehicle_id}_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Update vehicle with image URL
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        if not vehicle.image_urls:
            vehicle.image_urls = []
            
        image_url = f'/static/uploads/{filename}'
        vehicle.image_urls.append(image_url)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'image_url': image_url
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error uploading image: {str(e)}')
        return jsonify({'error': 'Failed to upload image'}), 500

@bp.route('/static/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded files"""
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        current_app.logger.error(f'Error serving file {filename}: {str(e)}')
        return jsonify({'error': 'File not found'}), 404

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
