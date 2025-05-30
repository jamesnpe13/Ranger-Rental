from flask_jwt_extended import JWTManager
from models.user import User

# Initialize JWT manager (will be initialized in app.py)
jwt = JWTManager()

def init_auth(app):
    """
    Initialize authentication with the Flask app.
    
    Args:
        app: Flask application instance
    """
    # Configure JWT
    app.config.setdefault('JWT_SECRET_KEY', 'your-secret-key-here')
    app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', 86400)  # 24 hours
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Register auth blueprint
    from . import routes
    app.register_blueprint(routes.bp, url_prefix='/api/auth')
    
    # JWT configuration callbacks
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        # If user is already an ID, return it directly
        if isinstance(user, int):
            return user
        # Otherwise, return the user's ID
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)
    
    return jwt