"""WSGI config for Ranger-Rental project.

This module contains the WSGI application used by the production server.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from app import create_app

# Set the default configuration
os.environ.setdefault('FLASK_ENV', 'production')

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    # This is only used when running locally. In production, a WSGI server like Gunicorn will be used.
    app.run(host='0.0.0.0', port=5000, debug=app.debug)
