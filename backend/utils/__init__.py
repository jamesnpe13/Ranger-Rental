"""
Utility functions and helpers.
"""
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models import User

def admin_required(f):
    """Decorator to ensure the user has admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_dates(start_date_str: str, end_date_str: str) -> tuple[bool, dict]:
    """Validate date range."""
    try:
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        
        if start_date >= end_date:
            return False, {"error": "End date must be after start date"}
            
        if (end_date - start_date).days > 30:
            return False, {"error": "Maximum booking duration is 30 days"}
            
        return True, {"start_date": start_date, "end_date": end_date}
        
    except (ValueError, TypeError) as e:
        return False, {"error": f"Invalid date format: {str(e)}"}

def calculate_total_price(price_per_day: float, start_date: datetime, end_date: datetime) -> float:
    """Calculate total price for a booking."""
    days = (end_date - start_date).days + 1  # Include both start and end days
    return price_per_day * days
