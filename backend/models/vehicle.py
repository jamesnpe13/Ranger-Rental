from . import db
from datetime import datetime

class Vehicle(db.Model):
    """Vehicle model for rental vehicles."""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'Sedan', 'SUV', 'Truck'
    price_per_day = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))  # Single image URL for simplicity
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # The relationship with Booking is defined in the Booking model
    
    def to_dict(self, include_owner=False):
        """Convert vehicle object to dictionary."""
        result = {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'type': self.type,
            'price_per_day': float(self.price_per_day) if self.price_per_day else None,
            'is_available': self.is_available,
            'location': self.location,
            'description': self.description,
            'image_url': self.image_url,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_owner and hasattr(self, 'owner') and self.owner:
            result['owner'] = {
                'id': self.owner.id,
                'email': self.owner.email,
                'first_name': getattr(self.owner, 'first_name', None),
                'last_name': getattr(self.owner, 'last_name', None)
            }
            
        return result
        
    def is_available_for_dates(self, start_date, end_date):
        """Check if vehicle is available for the given dates."""
        if not self.is_available:
            return False
            
        # Check for any overlapping bookings
        from .booking import Booking
        overlapping = Booking.query.filter(
            Booking.vehicle_id == self.id,
            Booking.status.in_(['pending', 'confirmed']),
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        ).first()
        
        return overlapping is None
        
    def update_availability(self, is_available):
        """Update vehicle availability."""
        self.is_available = is_available
        self.updated_at = datetime.utcnow()
        
    def __repr__(self):
        return f'<Vehicle {self.year} {self.make} {self.model}>'
    
    def check_availability(self, start_date=None, end_date=None):
        """
        Check if vehicle is available.
        If dates are provided, checks for booking conflicts.
        """
        # If no dates provided, just return the basic availability
        if not start_date or not end_date:
            return self.is_available
            
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
        if start_date >= end_date:
            return False
            
        # Check for any overlapping bookings
        from .booking import Booking
        
        overlapping = db.session.query(Booking).filter(
            Booking.vehicle_id == self.id,
            Booking.status == 'confirmed',
            or_(
                and_(
                    Booking.start_date <= start_date,
                    Booking.end_date >= start_date
                ),
                and_(
                    Booking.start_date <= end_date,
                    Booking.end_date >= end_date
                ),
                and_(
                    Booking.start_date >= start_date,
                    Booking.end_date <= end_date
                )
            )
        ).first()
        
        return self.is_available and overlapping is None
    

