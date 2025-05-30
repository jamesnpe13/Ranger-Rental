"""
Core package containing the application factory and configuration.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_session import Session
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()
session = Session()
login_manager = LoginManager()

def create_app(config_class='config.Config'):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    session.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from ..api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    return app
