"""
Service layer containing business logic.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from ..core import db
from ..models import User, Vehicle, Booking

class UserService:
    """Service for user-related operations."""
    
    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        user = User(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        user.password = user_data['password']
        db.session.add(user)
        db.session.commit()
        return user

class VehicleService:
    """Service for vehicle-related operations."""
    
    @staticmethod
    def create_vehicle(vehicle_data: Dict[str, Any], owner_id: int) -> Vehicle:
        """Create a new vehicle."""
        vehicle = Vehicle(
            make=vehicle_data['make'],
            model=vehicle_data['model'],
            year=vehicle_data['year'],
            type=vehicle_data['type'],
            price_per_day=vehicle_data['price_per_day'],
            location=vehicle_data['location'],
            description=vehicle_data.get('description', ''),
            owner_id=owner_id
        )
        db.session.add(vehicle)
        db.session.commit()
        return vehicle

class BookingService:
    """Service for booking-related operations."""
    
    @staticmethod
    def create_booking(booking_data: Dict[str, Any], user_id: int) -> Booking:
        """Create a new booking."""
        booking = Booking(
            vehicle_id=booking_data['vehicle_id'],
            user_id=user_id,
            start_date=booking_data['start_date'],
            end_date=booking_data['end_date'],
            total_price=booking_data.get('total_price', 0),
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()
        return booking
