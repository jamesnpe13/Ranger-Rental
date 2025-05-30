"""
API package - contains all API endpoints organized by domain.
"""

from flask import Blueprint

# Create the main API blueprint
api = Blueprint('api', __name__)

# Import all route modules to register them with the blueprint
# Using absolute imports to avoid circular imports
from api import auth, vehicles, bookings, admin

# Register blueprints with the API namespace
api.register_blueprint(auth.auth_bp, url_prefix='/auth')
# Uncomment and update these when the other blueprints are ready
# api.register_blueprint(vehicles.vehicles_bp, url_prefix='/vehicles')
# api.register_blueprint(bookings.bookings_bp, url_prefix='/bookings')
# api.register_blueprint(admin.admin_bp, url_prefix='/admin')
