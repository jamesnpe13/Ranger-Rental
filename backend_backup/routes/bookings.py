from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import os
from email.mime.text import MIMEText
import smtplib
from models import db, Booking, Vehicle, User
import sqlite3

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def update_database_schema():
    """Update the database schema to add new columns if they don't exist"""
    conn = None
    try:
        # Get the database URL from SQLAlchemy
        db_url = str(db.engine.url)
        print(f"Database URL: {db_url}")
        
        if not db_url:
            return False, "No database URL found in SQLAlchemy configuration"
        
        # Handle different SQLite URL formats
        if db_url.startswith('sqlite:///'):
            # Format: sqlite:////path/to/db.sqlite
            db_path = db_url[10:]  # Remove 'sqlite:///'
        elif db_url == 'sqlite:///:memory:':
            return False, "Cannot update an in-memory database. Please use a file-based database."
        elif db_url.startswith('sqlite://'):
            # Format: sqlite:///path/to/db.sqlite (with 3 slashes)
            db_path = db_url[9:]  # Remove 'sqlite://'
        else:
            return False, f"Unsupported database type: {db_url}. Only SQLite file-based databases are supported."
        
        # Handle Windows paths if needed
        if db_path.startswith('/'):
            # On Windows, the path might start with /C:/path/to/db.sqlite
            import platform
            if platform.system() == 'Windows':
                db_path = db_path[1:]  # Remove leading slash
        
        print(f"Database file path: {db_path}")
        
        # Use SQLAlchemy's connection for better path handling
        print("Connecting to SQLite database using SQLAlchemy engine...")
        with db.engine.connect() as connection:
            # Get raw DBAPI connection
            raw_connection = connection.connection
            cursor = raw_connection.cursor()
            
            # Check if the table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bookings';")
            if not cursor.fetchone():
                return False, "The 'bookings' table does not exist in the database"
            
            # Check which columns already exist
            cursor.execute("PRAGMA table_info(bookings);")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Existing columns: {columns}")
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION;")
            
            # Add columns if they don't exist
            if 'total_price' not in columns:
                print("Adding total_price column")
                cursor.execute("ALTER TABLE bookings ADD COLUMN total_price FLOAT DEFAULT 0.0;")
            
            if 'payment_intent_id' not in columns:
                print("Adding payment_intent_id column")
                cursor.execute("ALTER TABLE bookings ADD COLUMN payment_intent_id VARCHAR(100);")
            
            # Update status if needed
            cursor.execute("UPDATE bookings SET status = 'pending' WHERE status IS NULL;")
            
            # Commit changes
            raw_connection.commit()
            print("Database schema updated successfully")
            return True, "Database schema updated successfully"
            
    except sqlite3.Error as e:
        if 'raw_connection' in locals():
            raw_connection.rollback()
        print(f"SQLite error: {str(e)}")
        return False, f"SQLite error: {str(e)}"
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False, f"Unexpected error: {str(e)}"
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False, f"Unexpected error: {str(e)}"

# Mock email function (replace with actual email service in production)
def send_booking_confirmation(email, booking_details):
    """Mock function to send booking confirmation email"""
    print(f"\n=== EMAIL SENT TO: {email} ===")
    print(f"Subject: Your Booking Confirmation - {booking_details['booking_id']}")
    print(f"""
    Thank you for your booking!
    
    Booking ID: {booking_details['booking_id']}
    Vehicle: {booking_details['vehicle_make']} {booking_details['vehicle_model']}
    Dates: {booking_details['start_date']} to {booking_details['end_date']}
    Total: ${booking_details['total_price']:.2f}
    Status: {booking_details['status']}
    
    We look forward to serving you!
    """)
    print("=== END OF EMAIL ===\n")

bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@bp.route('', methods=['GET'])
@jwt_required()
def get_bookings():
    user_id = get_jwt_identity()
    status = request.args.get('status')
    
    # Start building the query
    query = Booking.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Execute the query and convert to dict
    bookings = query.all()
    return jsonify([{
        'id': b.id,
        'vehicle_id': b.vehicle_id,
        'start_date': b.start_date.isoformat(),
        'end_date': b.end_date.isoformat(),
        'total_price': float(b.total_price),
        'status': b.status,
        'created_at': b.created_at.isoformat() if b.created_at else None
    } for b in bookings])

@bp.route('/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create a payment intent for Stripe"""
    try:
        data = request.get_json()
        amount = int(float(data.get('amount', 0)) * 100)  # Convert to cents
        
        if amount < 50:  # Minimum amount in cents
            return jsonify({"error": "Amount must be at least $0.50"}), 400
            
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='nzd',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        return jsonify({
            'clientSecret': intent.client_secret
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()
    required_fields = ['vehicle_id', 'start_date', 'end_date']
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if start_date >= end_date:
            return jsonify({"error": "End date must be after start date"}), 400
            
        if start_date < datetime.now().date():
            return jsonify({"error": "Start date cannot be in the past"}), 400
            
        # Get vehicle with owner details
        vehicle = Vehicle.query.options(
            db.joinedload(Vehicle.owner)
        ).filter_by(
            id=data['vehicle_id'],
            is_available=True
        ).first()
        
        if not vehicle:
            return jsonify({"error": "Vehicle not available for booking"}), 400
        
        # Check for booking conflicts
        conflict = Booking.query.filter(
            Booking.vehicle_id == data['vehicle_id'],
            Booking.status == 'confirmed',
            db.or_(
                db.and_(Booking.start_date <= start_date, Booking.end_date >= start_date),
                db.and_(Booking.start_date <= end_date, Booking.end_date >= end_date),
                db.and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
            )
        ).first()
        
        if conflict:
            return jsonify({"error": "Vehicle is already booked for the selected dates"}), 400
        
        # Calculate total price and days
        days = (end_date - start_date).days + 1  # Include both start and end dates
        total_price = days * vehicle.price_per_day
        
        # Create booking without payment processing
        booking = Booking(
            user_id=user_id,
            vehicle_id=data['vehicle_id'],
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='confirmed',
            payment_intent_id='offline_payment'
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send booking confirmation (mock)
        send_booking_confirmation(booking.user.email, {
            'booking_id': booking.id,
            'vehicle_make': vehicle.make,
            'vehicle_model': vehicle.model,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'total_price': total_price,
            'status': 'confirmed'
        })
        
        return jsonify({
            "message": "Booking created successfully", 
            "booking_id": booking.id,
            "total_price": total_price,
            "days": days,
            "status": "confirmed"
        }), 201
            
    except ValueError as e:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the requesting user owns the booking
    if booking.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    return jsonify({
        'id': booking.id,
        'vehicle_id': booking.vehicle_id,
        'start_date': booking.start_date.isoformat(),
        'end_date': booking.end_date.isoformat(),
        'total_price': float(booking.total_price),
        'status': booking.status,
        'created_at': booking.created_at.isoformat() if booking.created_at else None
    })

@bp.route('/<int:booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    try:
        # Get the booking and verify ownership
        booking = Booking.query.get_or_404(booking_id)
        if booking.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Update fields if provided
        if 'start_date' in data:
            booking.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            
        if 'end_date' in data:
            booking.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            
        if 'status' in data:
            # Only allow certain status updates
            if data['status'] in ['cancelled']:
                booking.status = data['status']
            
        db.session.commit()
        
        return jsonify({
            'id': booking.id,
            'status': booking.status,
            'message': 'Booking updated successfully'
        })
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:booking_id>', methods=['DELETE'])
@jwt_required()
def delete_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure the requesting user owns the booking
    if booking.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        if booking.status in ['confirmed', 'active']:
            return jsonify({"error": "Cannot delete a confirmed or active booking"}), 400
            
        db.session.delete(booking)
        db.session.commit()
        return jsonify({"message": "Booking deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/update-db-schema', methods=['POST'])
@jwt_required()
def update_db_schema():
    """Endpoint to update the database schema"""
    try:
        success, message = update_database_schema()
        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to update database schema: {str(e)}"}), 500
