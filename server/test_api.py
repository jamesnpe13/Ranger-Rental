import unittest
import json
import os
import tempfile
from flask import Flask
from models import db, User, Vehicle, Booking
from datetime import datetime, timedelta
from auth import init_auth, jwt
from flask_login import LoginManager

class VehicleAPITestCase(unittest.TestCase):
    """Test cases for the Vehicle API endpoints."""

    def create_app(self):
        """Create and configure the test app."""
        # Create a test app with in-memory SQLite database
        app = Flask(__name__)
        
        # Configure the app for testing
        app.config.update(
            TESTING=True,
            DEBUG=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            WTF_CSRF_ENABLED=False,  # Disable CSRF for testing
            SECRET_KEY='test-secret-key',
            SESSION_TYPE='filesystem',
            SESSION_COOKIE_SECURE=False,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            UPLOAD_FOLDER=os.path.join(os.path.dirname(__file__), 'test_uploads'),
            PROPAGATE_EXCEPTIONS=True,
            JWT_SECRET_KEY='test-jwt-secret',
            JWT_ACCESS_TOKEN_EXPIRES=3600,
            JWT_TOKEN_LOCATION=['headers', 'cookies'],
            JWT_COOKIE_SECURE=False,
            JWT_COOKIE_CSRF_PROTECT=False
        )
        
        # Initialize extensions
        db.init_app(app)
        jwt.init_app(app)
        
        # Initialize Flask-Login
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
        
        # Register blueprints with proper URL prefixes
        from routes.vehicles import bp as vehicles_bp
        from routes.bookings import bp as bookings_bp
        from auth.routes import bp as auth_bp
        
        app.register_blueprint(vehicles_bp, url_prefix='/api/vehicles')
        app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        return app

    def setUp(self):
        """Set up test variables and initialize app."""
        # Create the app
        self.app = self.create_app()
        self.client = self.app.test_client()
        
        # Push an application context
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Create test database and tables
        with self.app.app_context():
            # Drop all tables first to ensure a clean state
            db.drop_all()
            # Create all tables
            db.create_all()
            # Create test data
            self.create_test_data()
            # Commit the session to save the test data
            db.session.commit()
    
    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.ctx.pop()

    def create_test_data(self):
        """Create test data in the database."""
        # Create test user
        user = User(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='admin',  # Set role to 'admin' instead of is_admin
            is_active=True
        )
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID

        # Create test vehicle
        vehicle = Vehicle(
            make='Toyota',
            model='Camry',
            year=2022,
            type='Sedan',
            price_per_day=50.00,
            is_available=True,
            location='Test Location',
            description='Test Description',
            owner_id=user.id,
            image_urls=[]  # Initialize with empty list
        )
        db.session.add(vehicle)
        db.session.flush()  # Flush to get the vehicle ID

        # Create test booking
        start_date = datetime.utcnow() + timedelta(days=1)
        end_date = start_date + timedelta(days=3)
        booking = Booking(
            vehicle_id=vehicle.id,
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
            total_price=150.00,
            status='confirmed',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(booking)

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_auth_headers(self, email, password):
        """Helper method to get auth token for a user."""
        response = self.client.post(
            '/api/auth/login',
            json={
                'email': email,
                'password': password
            }
        )
        data = json.loads(response.data)
        return {'Authorization': f"Bearer {data['access_token']}"}

    def test_get_vehicles(self):
        """Test GET /api/vehicles endpoint."""
        with self.app.app_context():
            # Get auth token for the test user
            headers = self.get_auth_headers('test@example.com', 'testpass123')
            
            # Make the request with auth header
            response = self.client.get(
                '/api/vehicles',
                headers=headers
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('vehicles', data)
            self.assertGreater(len(data['vehicles']), 0)

    def test_get_vehicle(self):
        """Test GET /api/vehicles/<id> endpoint."""
        with self.app.app_context():
            # Get auth token for the test user
            headers = self.get_auth_headers('test@example.com', 'testpass123')
            
            # Get a vehicle
            vehicle = Vehicle.query.first()
            response = self.client.get(
                f'/api/vehicles/{vehicle.id}',
                headers=headers
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('vehicle', data)
            self.assertEqual(data['vehicle']['id'], vehicle.id)

    def test_check_availability(self):
        """Test GET /api/vehicles/<id>/availability endpoint."""
        with self.app.app_context():
            # Get auth token for the test user
            headers = self.get_auth_headers('test@example.com', 'testpass123')
            
            # Get a vehicle
            vehicle = Vehicle.query.first()
            
            # Test availability
            start_date = (datetime.utcnow() + timedelta(days=10)).strftime('%Y-%m-%d')
            end_date = (datetime.utcnow() + timedelta(days=13)).strftime('%Y-%m-%d')
            
            response = self.client.get(
                f'/api/vehicles/{vehicle.id}/availability',
                query_string={
                    'start_date': start_date,
                    'end_date': end_date
                },
                headers=headers
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('available', data)
            self.assertTrue(data['available'])

    def test_list_routes(self):
        """List all available routes for debugging."""
        with self.app.app_context():
            # Print all routes from the URL map
            print("\n=== Available Routes ===")
            for rule in sorted(self.app.url_map.iter_rules(), key=lambda r: r.rule):
                methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                print(f"{rule.endpoint:40} {methods:20} {rule}")
            
            # Print blueprints
            print("\n=== Registered Blueprints ===")
            for name, bp in self.app.blueprints.items():
                print(f"{name}:")
                print(f"  URL Prefix: {bp.url_prefix}")
                print(f"  Static Folder: {bp.static_folder}")
                print(f"  Template Folder: {bp.template_folder}")
            
            # Print extensions
            print("\n=== Extensions ===")
            for ext_name, ext in self.app.extensions.items():
                print(f"{ext_name}: {ext}")
            
    def test_vehicle_search(self):
        """Test vehicle search functionality."""
        with self.app.app_context():
            # Get auth token for the test user
            headers = self.get_auth_headers('test@example.com', 'testpass123')
            
            # Test search
            response = self.client.get(
                '/api/vehicles',
                query_string={'make': 'Toyota', 'type': 'Sedan'},
                headers=headers
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('success', data)
            self.assertTrue(data['success'])
            self.assertIn('vehicles', data)
            self.assertGreater(len(data['vehicles']), 0)
            self.assertEqual(data['vehicles'][0]['make'], 'Toyota')
            self.assertEqual(data['vehicles'][0]['type'], 'Sedan')

if __name__ == '__main__':
    unittest.main()
