from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy with session options
db = SQLAlchemy(session_options={
    'expire_on_commit': False
})

def init_app(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    with app.app_context():
        # Import models here to avoid circular imports
        from .user import User
        from .vehicle import Vehicle
        from .booking import Booking
        from .payment import Payment
    
    return db