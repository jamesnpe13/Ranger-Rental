import os

class Config:
    # Database configuration
    DATABASE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ranger_rental.db')
    
    # Application configuration
    DEBUG = os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 't']
    HOST = os.environ.get('APP_HOST', '127.0.0.1')
    PORT = int(os.environ.get('APP_PORT', 5000))
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Logging
    LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
    LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'

class TestConfig(Config):
    TESTING = True
    DATABASE_FILE = ':memory:'  # Use in-memory database for tests

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Production-specific initialization can go here

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
