# Ranger-Rental Backend

This is the backend service for the Ranger-Rental application, built with Flask and SQLAlchemy.

## Project Structure

```
backend/
├── api/                   # API endpoints organized by domain
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   ├── vehicles.py        # Vehicle management routes
│   ├── bookings.py        # Booking management routes
│   └── admin.py           # Admin-only routes
├── models/                # Database models
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── vehicle.py         # Vehicle model
│   └── booking.py         # Booking model
├── schemas/               # Data validation schemas
│   └── __init__.py
├── services/              # Business logic
│   └── __init__.py
├── utils/                 # Helper functions and utilities
│   └── __init__.py
├── config.py              # Application configuration
├── wsgi.py                # WSGI entry point
└── requirements.txt       # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- PostgreSQL (or SQLite for development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ranger-rental.git
   cd ranger-rental/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

### Running the Application

#### Development Mode

```bash
flask run
```

The server will start at `http://localhost:5000`.

#### Production Mode

For production, it's recommended to use a production WSGI server like Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:5000/api/docs`
- ReDoc: `http://localhost:5000/api/redoc`

## Testing

To run the test suite:

```bash
pytest
```

## Code Style

This project uses:
- Black for code formatting
- Flake8 for linting
- isort for import sorting

Run the following commands before committing:

```bash
black .
isort .
flake8
```

## Deployment

### Heroku

1. Create a new Heroku app:
   ```bash
   heroku create
   ```

2. Set up the database:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. Deploy the application:
   ```bash
   git push heroku main
   ```

4. Run migrations:
   ```bash
   heroku run flask db upgrade
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
