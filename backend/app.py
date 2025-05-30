from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import os
from functools import wraps

# Import db from models to avoid circular imports
from models import db, init_app as init_models

# Initialize JWT
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ranger_rentals.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    # Initialize extensions
    init_models(app)  # Initialize models and database
    jwt.init_app(app)
    CORS(app)
    
    # Import models after db is initialized
    from models.user import User
    from models.vehicle import Vehicle
    from models.booking import Booking
    from models.payment import Payment
    
    # Import and register blueprints
    from api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    # Create database tables and admin user
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        try:
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(email='admin@ranger.com').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@ranger.com',
                    password=generate_password_hash('admin123'),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {str(e)}")
    
    # Simple test route
    @app.route('/')
    def home():
        return jsonify({"message": "Welcome to Ranger Rentals API"})
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
