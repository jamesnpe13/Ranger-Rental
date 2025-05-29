from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()

# Import models after db to avoid circular imports
from .user import User
from .vehicle import Vehicle
from .booking import Booking