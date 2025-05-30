import os
import logging
from datetime import timedelta
from flask import Flask, jsonify, request, redirect, url_for, render_template_string, render_template, session
from flask_cors import CORS
from flask_session import Session
from flask_login import LoginManager, current_user, login_required
from auth import init_auth, jwt
from models import db, bcrypt, User, Vehicle, Booking
from vehicles import bp as vehicles_bp
from routes.availability import bp as availability_bp
from routes.bookings import bp as bookings_bp
from admin_dashboard import bp as admin_ui_bp, init_login_manager
from routes.admin_routes import bp as admin_api_bp

def create_app():
    # Initialize Flask app with debug mode
    app = Flask(__name__, 
                template_folder=os.path.abspath('../frontend'),
                static_folder=os.path.abspath('../frontend/static'))
    
    # Enable debug mode and detailed error messages
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['TRAP_HTTP_EXCEPTIONS'] = True
    
    # Configure upload folder
    UPLOAD_FOLDER = os.path.abspath(os.path.join(app.root_path, '..', 'frontend', 'static', 'uploads'))
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Register a route to serve the main index.html
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    app.config['DEBUG'] = True  # Enable debug mode for detailed error messages
    
    # Flask-Login initialization is now handled later in the file
    
    # Load configuration from environment variables
    app.config.update(
        # Application
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
        
        # Session configuration
        SESSION_TYPE='filesystem',
        SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=1),  # Session expires after 1 day
        
        # Database configuration
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///ranger_rental.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ECHO=os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true',
        
        # JWT Configuration
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'your-secret-key-here'),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24),  # 24 hours
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),  # 30 days
        JWT_TOKEN_LOCATION=['headers'],
        JWT_HEADER_NAME='Authorization',
        JWT_HEADER_TYPE='Bearer',
        JWT_ACCESS_COOKIE_NAME='access_token_cookie',
        JWT_REFRESH_COOKIE_NAME='refresh_token_cookie',
        JWT_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production',
        JWT_COOKIE_CSRF_PROTECT=True,
        JWT_CSRF_CHECK_FORM=True,
        
        # Security
        PASSWORD_RESET_EXPIRATION=3600  # 1 hour
    )

    # Configure CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:3000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "expose_headers": ["Content-Type", "Content-Disposition"]
            }
        }
    )

    # Configure logging
    debug_mode = os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 't']
    log_level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app.logger.setLevel(log_level)

    # Configure secret key for session management - must be set before initializing extensions
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-this-in-production')
    
    # Configure session to use filesystem and set other session options
    app.config.update(
        SESSION_TYPE='filesystem',
        SESSION_FILE_DIR=os.path.join(app.instance_path, 'flask_session'),
        SESSION_FILE_THRESHOLD=100,  # Maximum number of sessions before cleanup
        SESSION_USE_SIGNER=True,  # Sign the session cookie
        SESSION_COOKIE_SECURE=False,  # Should be True in production with HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=1),  # Session expires after 1 day
    )
    
    # Ensure the session directory exists
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    
    # Initialize Flask-Session
    Session(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    # login_view is now set in init_login_manager
    init_login_manager(login_manager)
    
    # Initialize authentication and register auth blueprint
    init_auth(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Configure template and static folders for admin UI blueprint
    admin_ui_bp.template_folder = os.path.abspath('../frontend/admin')
    admin_ui_bp.static_folder = os.path.abspath('../frontend/static')
    
    # Register blueprints with proper URL prefixes
    app.register_blueprint(vehicles_bp, url_prefix='/api/vehicles')
    app.register_blueprint(availability_bp, url_prefix='/api/availability')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    
    # Register admin blueprints with proper prefixes
    app.register_blueprint(admin_ui_bp, url_prefix='/admin')
    app.register_blueprint(admin_api_bp)  # Already has /api/v1/admin prefix
    
    # Route to list all routes
    @app.route('/routes')
    def list_routes():
        try:
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(f"{rule.endpoint}: {rule.methods} -> {rule}")
            return jsonify({
                'success': True,
                'routes': routes
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Simple home route
    @app.route('/')
    def home():
        return '''
        <h1>Ranger Rental API</h1>
        <p><a href='/admin/'>Admin Dashboard</a></p>
        <p><a href='/routes'>View All Routes</a></p>
        <p><a href='/api/vehicles'>Vehicles API</a></p>
        <p><a href='/api/bookings'>Bookings API</a></p>
        <p><a href='/api/admin/users'>Admin Users API</a> (requires auth)</p>
        '''
        return jsonify({
            'message': 'Welcome to the Ranger-Rental API',
            'status': 'operational',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'refresh': 'POST /api/auth/refresh',
                    'me': 'GET /api/auth/me',
                    'update_me': 'PUT /api/auth/me'
                },
                'admin': {
                    'list_users': 'GET /api/auth/admin/users',
                    'get_user': 'GET /api/auth/admin/users/<int:user_id>',
                    'update_user': 'PUT /api/auth/admin/users/<int:user_id>',
                    'delete_user': 'DELETE /api/auth/admin/users/<int:user_id>'
                }
            }
        })
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': str(error) or 'Bad Request',
                'status': 400
            }
        }), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': 'Authentication required',
                'status': 401
            }
        }), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': 'You do not have permission to access this resource',
                'status': 403
            }
        }), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found',
                'status': 404
            }
        }), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': 'The method is not allowed for the requested URL',
                'status': 405
            }
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNPROCESSABLE_ENTITY',
                'message': 'The request was well-formed but was unable to be followed due to semantic errors',
                'status': 422,
                'details': str(error)
            }
        }), 422

    @app.errorhandler(429)
    def too_many_requests_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOO_MANY_REQUESTS',
                'message': 'Too many requests, please try again later',
                'status': 429,
                'retry_after': getattr(error, 'retry_after', None)
            }
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred',
                'status': 500
            }
        }), 500

    # Handle SQLAlchemy errors
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}', exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred',
                'status': 500
            }
        }), 500

    # Request logging
    @app.before_request
    def log_request_info():
        if request.method != 'OPTIONS':  # Skip logging for OPTIONS requests
            app.logger.debug(f'Request: {request.method} {request.path} - Headers: {dict(request.headers)}')

    @app.after_request
    def log_response(response):
        if request.method != 'OPTIONS':
            app.logger.debug(f'Response: {response.status} - {response.get_json()}')
        return response
    
    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 't']
    )
