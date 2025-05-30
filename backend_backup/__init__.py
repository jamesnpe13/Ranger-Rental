from flask import Flask
from flask_cors import CORS
from config import config

def create_app(config_name='default'):
    """Application factory function to create and configure the Flask app."""
    app = Flask(__name__)
    
    # Apply configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', '*'),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    from .routes.auth import bp as auth_bp
    from .routes.vehicles import bp as vehicles_bp
    from .routes.bookings import bp as bookings_bp
    from .routes.payments import bp as payments_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    
    # Register error handlers
    from .utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # Initialize database
    from .models import init_db
    init_db()
    
    return app
