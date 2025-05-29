from datetime import datetime
from models import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_intent_id = db.Column(db.String(100), unique=True, nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle = db.relationship('Vehicle', backref='bookings')
    user = db.relationship('User', backref='bookings')
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'total_price': float(self.total_price) if self.total_price else None,
            'payment_intent_id': self.payment_intent_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def is_vehicle_available(cls, vehicle_id, start_date, end_date):
        """Check if a vehicle is available for the given date range"""
        from sqlalchemy import and_, or_
        
        # Convert string dates to datetime objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
            
        # Check for any overlapping bookings
        overlapping_booking = cls.query.filter(
            cls.vehicle_id == vehicle_id,
            cls.status == 'confirmed',  # Only consider confirmed bookings
            or_(
                # Existing booking starts during the requested period
                and_(
                    cls.start_date >= start_date,
                    cls.start_date < end_date
                ),
                # Existing booking ends during the requested period
                and_(
                    cls.end_date > start_date,
                    cls.end_date <= end_date
                ),
                # Existing booking completely contains the requested period
                and_(
                    cls.start_date <= start_date,
                    cls.end_date >= end_date
                )
            )
        ).first()
        
        return overlapping_booking is None
