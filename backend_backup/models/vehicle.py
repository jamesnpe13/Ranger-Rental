from models import db
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
    image_url = db.Column(db.String(255))
    
    # Relationships
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner = db.relationship('User', backref='vehicles')
    
    def to_dict(self):
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'type': self.type,
            'price_per_day': self.price_per_day,
            'is_available': self.is_available,
            'location': self.location,
            'description': self.description,
            'image_url': self.image_url
        }
