"""
WSGI entry point for the Ranger-Rental application.
"""
import os
from . import create_app

# Create the Flask application
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    # Run the Flask development server
    app.run(host=app.config.get('HOST', '0.0.0.0'),
            port=app.config.get('PORT', 5000),
            debug=app.config.get('DEBUG', False))
