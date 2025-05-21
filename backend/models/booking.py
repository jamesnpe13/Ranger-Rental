from datetime import datetime, timedelta
from models import db
from sqlalchemy import and_, or_

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
    
    def to_dict(self, include_vehicle=False, include_user=False):
        """Convert booking to dictionary with optional related objects"""
        result = {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_price': float(self.total_price) if self.total_price else None,
            'payment_intent_id': self.payment_intent_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'duration_days': (self.end_date - self.start_date).days if self.end_date and self.start_date else 0
        }
        
        if include_vehicle and self.vehicle:
            result['vehicle'] = self.vehicle.to_dict()
            
        if include_user and self.user:
            result['user'] = {
                'id': self.user.id,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
            }
            
        return result
    
    @classmethod
    def is_vehicle_available(cls, vehicle_id, start_date, end_date):
        """
        Check if a vehicle is available for the given date range
        
        Args:
            vehicle_id: ID of the vehicle to check
            start_date: Start date (datetime or ISO format string)
            end_date: End date (datetime or ISO format string)
            
        Returns:
            bool: True if vehicle is available, False otherwise
        """
        # Convert string dates to datetime objects if needed
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)
            
        # Check for invalid date range
        if start_date >= end_date:
            return False
            
        # Check for any overlapping bookings
        overlapping_booking = cls.query.filter(
            cls.vehicle_id == vehicle_id,
            cls.status.in_(['confirmed', 'pending']),  # Consider both confirmed and pending bookings
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
        
    @classmethod
    def get_vehicle_bookings(cls, vehicle_id, start_date=None, end_date=None, status=None):
        """
        Get all bookings for a vehicle, optionally filtered by date range and status
        """
        query = cls.query.filter_by(vehicle_id=vehicle_id)
        
        if status:
            if isinstance(status, str):
                status = [status]
            query = query.filter(cls.status.in_(status))
            
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.fromisoformat(start_date)
            query = query.filter(cls.end_date >= start_date)
            
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date)
            query = query.filter(cls.start_date <= end_date)
            
        return query.order_by(cls.start_date.asc()).all()
        
    def calculate_total_price(self, vehicle=None):
        """Calculate total price based on vehicle's daily rate and booking duration"""
        if not self.start_date or not self.end_date:
            return 0
            
        if not vehicle and not self.vehicle:
            return 0
            
        vehicle = vehicle or self.vehicle
        days = (self.end_date - self.start_date).days
        return days * (vehicle.price_per_day or 0)
        
    def cancel(self):
        """Cancel this booking"""
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return True
