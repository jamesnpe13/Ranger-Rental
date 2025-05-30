from models import db
from sqlalchemy import or_, and_
from datetime import datetime
from .user import User  # Import User model for relationship

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'Sedan', 'SUV', 'Truck'
    price_per_day = db.Column(db.Float, nullable=False)
    is_available = db.Column('is_available', db.Boolean, default=True, nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_urls = db.Column(db.JSON, default=list)  # Store multiple image URLs
    
    # Relationships
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', backref='vehicles')
    
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
    
    def to_dict(self, include_owner=False):
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
            'image_urls': self.image_urls or []
        }
        
        if include_owner and self.owner:
            result['owner'] = {
                'id': self.owner.id,
                'email': self.owner.email,
                'first_name': self.owner.first_name,
                'last_name': self.owner.last_name
            }
            
        return result
