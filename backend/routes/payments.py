from flask import Blueprint, request, jsonify
from models import get_db_connection

bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@bp.route('', methods=['GET'])
def get_payments():
    booking_id = request.args.get('booking_id', type=int)
    
    query = 'SELECT * FROM payments WHERE 1=1'
    params = []
    
    if booking_id is not None:
        query += ' AND booking_id = ?'
        params.append(booking_id)
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        payments = [dict(row) for row in cursor.fetchall()]
        return jsonify(payments)
    finally:
        conn.close()

@bp.route('', methods=['POST'])
def create_payment():
    data = request.get_json()
    required_fields = ['booking_id', 'amount', 'payment_method']
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Verify booking exists and get amount
        cursor.execute('SELECT total_price FROM bookings WHERE id = ?', (data['booking_id'],))
        booking = cursor.fetchone()
        
        if not booking:
            return jsonify({"error": "Booking not found"}), 404
            
        # In a real app, you would integrate with a payment gateway here
        # For this example, we'll just create a payment record
        
        cursor.execute(
            '''
            INSERT INTO payments 
            (booking_id, amount, payment_method, transaction_id, status)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                data['booking_id'],
                data['amount'],
                data['payment_method'],
                data.get('transaction_id'),  # In a real app, this would come from the payment gateway
                'completed'  # In a real app, this would depend on the payment gateway response
            )
        )
        
        payment_id = cursor.lastrowid
        
        # Update booking status to confirmed
        cursor.execute(
            'UPDATE bookings SET status = ? WHERE id = ?',
            ('confirmed', data['booking_id'])
        )
        
        conn.commit()
        return jsonify({"message": "Payment processed successfully", "payment_id": payment_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        
        if payment is None:
            return jsonify({"error": "Payment not found"}), 404
            
        return jsonify(dict(payment))
    finally:
        conn.close()

@bp.route('/<int:payment_id>/refund', methods=['POST'])
def refund_payment(payment_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get payment details
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        
        if not payment:
            return jsonify({"error": "Payment not found"}), 404
            
        if payment['status'] != 'completed':
            return jsonify({"error": "Only completed payments can be refunded"}), 400
            
        # In a real app, you would integrate with a payment gateway to process the refund
        # For this example, we'll just update the payment status
        
        cursor.execute(
            'UPDATE payments SET status = ? WHERE id = ?',
            ('refunded', payment_id)
        )
        
        # Update booking status to cancelled
        cursor.execute(
            'UPDATE bookings SET status = ? WHERE id = ?',
            ('cancelled', payment['booking_id'])
        )
        
        conn.commit()
        return jsonify({"message": "Refund processed successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
