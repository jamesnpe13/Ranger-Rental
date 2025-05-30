from datetime import datetime, timedelta
from sqlalchemy import or_, and_
from . import db

class Booking(db.Model):
    """Booking model for vehicle reservations."""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'confirmed', 'cancelled', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    vehicle = db.relationship('Vehicle', backref=db.backref('bookings', lazy=True))
    payments = db.relationship('Payment', backref='booking', lazy=True)
    
    def to_dict(self):
        """Convert booking to dictionary."""
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'total_price': float(self.total_price),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'duration_days': (self.end_date - self.start_date).days
        }
        
    def is_available(self):
        """Check if the booking dates are available."""
        from datetime import datetime
        now = datetime.utcnow()
        return self.start_date > now and self.status in ['pending', 'confirmed']
    
    def cancel(self):
        """Cancel the booking."""
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()
        
    def complete(self):
        """Mark the booking as completed."""
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
        
    def __repr__(self):
        return f'<Booking {self.id} - {self.start_date} to {self.end_date}>'
    
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
