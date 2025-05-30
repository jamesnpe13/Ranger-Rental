from . import db
from datetime import datetime

class Payment(db.Model):
    """Payment model for handling payment transactions."""
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., 'credit_card', 'paypal'
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'completed', 'failed', 'refunded'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, user_id, booking_id, amount, payment_method, status='pending'):
        self.user_id = user_id
        self.booking_id = booking_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = status
        self.transaction_id = f"TXN{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    def to_dict(self):
        """Convert payment object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'booking_id': self.booking_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<Payment {self.transaction_id} - {self.amount}>'
