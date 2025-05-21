import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db
from app import create_app

def upgrade():
    """Create the bookings table"""
    app = create_app()
    with app.app_context():
        # This will create all tables that don't exist yet
        db.create_all()
        print("Created bookings table")

if __name__ == '__main__':
    upgrade()

