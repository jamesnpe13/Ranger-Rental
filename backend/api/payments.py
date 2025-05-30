from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.payment import Payment
from models.booking import Booking
from models.user import User
from datetime import datetime

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    """Get all payments (admin only)"""
    # Check if user is admin
    current_user_id = get_jwt_identity()
    if not User.query.get(current_user_id).is_admin:
        return jsonify({"error": "Admin access required"}), 403
        
    payments = Payment.query.all()
    return jsonify({
        'success': True,
        'payments': [{
            'id': p.id,
            'booking_id': p.booking_id,
            'amount': str(p.amount),
            'status': p.status,
            'payment_method': p.payment_method,
            'transaction_id': p.transaction_id,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None
        } for p in payments]
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_payment():
    """Create a new payment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided in request body',
                'request_data': str(request.data),
                'content_type': request.content_type
            }), 400
            
        print("\n=== Payment Request ===")
        print(f"Request data: {data}")
        print(f"Headers: {dict(request.headers)}")
        
        # Validate required fields
        required_fields = ['booking_id', 'amount', 'payment_method']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'received_data': data
            }), 400
            
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        print(f"Current user: {current_user_id}, is_admin: {getattr(current_user, 'is_admin', False)}")
        
        # Verify booking exists
        booking = Booking.query.get(data['booking_id'])
        print(f"Found booking: {booking}")
        
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found',
                'booking_id': data['booking_id']
            }), 404
        
        # Check if user is authorized
        if booking.user_id != current_user_id and not getattr(current_user, 'is_admin', False):
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'booking_user_id': booking.user_id,
                'current_user_id': current_user_id,
                'is_admin': getattr(current_user, 'is_admin', False)
            }), 403
            
        # Create new payment
        try:
            # Create payment with required fields
            payment = Payment(
                user_id=current_user_id,
                booking_id=data['booking_id'],
                amount=float(data['amount']),
                payment_method=data['payment_method'],
                status='completed'
            )
            # Set transaction_id after creation since it's auto-generated
            payment.transaction_id = data.get('transaction_id') or f"TXN{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            print(f"Created payment: {payment}")
            
            # Update booking status
            booking.status = 'confirmed'
            print(f"Updated booking status to: {booking.status}")
            
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'payment_id': payment.id,
                'message': 'Payment processed successfully',
                'status': payment.status,
                'transaction_id': payment.transaction_id,
                'booking_status': booking.status
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating payment: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Error creating payment: {str(e)}',
                'exception_type': type(e).__name__
            }), 500
        
    except Exception as e:
        print(f"Unexpected error in create_payment: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'exception_type': type(e).__name__
        }), 500

@bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get payment details by ID"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Check if the current user is the owner of the booking or an admin
    current_user_id = get_jwt_identity()
    if payment.booking.user_id != current_user_id and not User.query.get(current_user_id).is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    return jsonify({
        'id': payment.id,
        'booking_id': payment.booking_id,
        'amount': float(payment.amount),
        'status': payment.status,
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'created_at': payment.created_at.isoformat(),
        'updated_at': payment.updated_at.isoformat() if payment.updated_at else None
    })

@bp.route('/booking/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking_payments(booking_id):
    """Get all payments for a booking"""
    booking = Booking.query.get_or_404(booking_id)
    current_user_id = get_jwt_identity()
    
    # Check if the current user is the owner of the booking or an admin
    if booking.user_id != current_user_id and not User.query.get(current_user_id).is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    payments = Payment.query.filter_by(booking_id=booking_id).all()
    
    return jsonify([{
        'id': p.id,
        'booking_id': p.booking_id,
        'amount': float(p.amount),
        'status': p.status,
        'payment_method': p.payment_method,
        'transaction_id': p.transaction_id,
        'created_at': p.created_at.isoformat(),
        'updated_at': p.updated_at.isoformat() if p.updated_at else None
    } for p in payments])

@bp.route('/<int:payment_id>/refund', methods=['POST'])
@jwt_required()
def refund_payment(payment_id):
    """Refund a payment"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Check if user is authorized
    current_user_id = get_jwt_identity()
    if payment.booking.user_id != current_user_id and not User.query.get(current_user_id).is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    if payment.status != 'completed':
        return jsonify({
            'success': False,
            'error': 'Only completed payments can be refunded'
        }), 400
    
    try:
        # Update payment status to refunded
        payment.status = 'refunded'
        payment.updated_at = datetime.utcnow()
        
        # Update booking status to refunded
        booking = Booking.query.get(payment.booking_id)
        if booking:
            booking.status = 'refunded'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment refunded successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
