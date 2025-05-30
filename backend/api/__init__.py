from flask import Blueprint

# Create the main API blueprint
api = Blueprint('api', __name__)

# Import and register blueprints
from . import auth
from . import payments
from . import vehicles
from . import bookings

# Register blueprints
api.register_blueprint(auth.auth_bp, url_prefix='/auth')
api.register_blueprint(payments.bp, url_prefix='/payments')
api.register_blueprint(vehicles.bp, url_prefix='/vehicles')
api.register_blueprint(bookings.bp, url_prefix='/bookings')
