# Ranger-Rental API Backend

This backend provides a RESTful API for managing car rentals for the Ranger-Rental application. It uses Flask for the web framework and SQLite for data persistence.

## Project Structure

```
backend/
├── __init__.py         # Application factory and main package
├── config.py           # Configuration settings
├── wsgi.py             # WSGI entry point
├── requirements.txt    # Project dependencies
├── models/             # Database models and initialization
│   └── __init__.py
├── routes/             # API routes
│   ├── __init__.py
│   ├── auth.py         # Authentication routes
│   ├── vehicles.py     # Vehicle management routes
│   ├── bookings.py     # Booking management routes
│   └── payments.py     # Payment processing routes
└── utils/              # Utility functions
    └── errors.py       # Error handlers
```

## Features

* User authentication and authorization
* Vehicle management (CRUD operations)
* Booking management
* Payment processing
* Input validation
* Consistent JSON error responses
* Configurable via environment variables
* Request/response logging
* SQLite database with proper schema and relationships

## Setup and Running

1. **Clone the repository and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional):**
   Create a `.env` file in the backend directory with your configuration:
   ```
   FLASK_DEBUG=1
   APP_HOST=0.0.0.0
   APP_PORT=5000
   SECRET_KEY=your-secret-key
   ```

5. **Run the application:**
   ```bash
   python -m flask run
   # or for development with auto-reload:
   FLASK_DEBUG=1 python -m flask run
   ```

The API will be available at `http://<host>:<port>/api` (default `http://127.0.0.1:5000/api`).

## API Documentation

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get an authentication token

### Vehicles

- `GET /api/vehicles` - List all vehicles (with optional filters)
- `POST /api/vehicles` - Add a new vehicle
- `GET /api/vehicles/<id>` - Get vehicle details
- `PUT /api/vehicles/<id>` - Update a vehicle
- `DELETE /api/vehicles/<id>` - Delete a vehicle

### Bookings

- `GET /api/bookings` - List all bookings (with optional filters)
- `POST /api/bookings` - Create a new booking
- `GET /api/bookings/<id>` - Get booking details
- `PUT /api/bookings/<id>` - Update a booking status
- `DELETE /api/bookings/<id>` - Cancel a booking

### Payments

- `GET /api/payments` - List all payments (with optional filters)
- `POST /api/payments` - Process a payment
- `GET /api/payments/<id>` - Get payment details
- `POST /api/payments/<id>/refund` - Process a refund

## Configuration

The application can be configured using the following environment variables:

- `FLASK_DEBUG`: Enable debug mode (`1` or `true`)
- `APP_HOST`: Host to bind to (default: `127.0.0.1`)
- `APP_PORT`: Port to listen on (default: `5000`)
- `SECRET_KEY`: Secret key for session security
- `DATABASE_URL`: Database connection URL (default: SQLite database at `ranger_rental.db`)

## Development

### Running Tests

To run the test suite:

```bash
python -m pytest
```

### Database Migrations

For database schema changes, use Flask-Migrate:

```bash
flask db migrate -m "description of changes"
flask db upgrade
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
    *   Example: `export APP_HOST=0.0.0.0`
*   `APP_PORT`: The port the server will listen on. Defaults to `5000`.
    *   Example: `export APP_PORT=8000`

## API Endpoints

The API provides the following endpoints for managing car rental items:

### Cars (`/api/items`)

*   `GET /`: Welcome message.
*   `GET /api/items`: Returns a list of all rental cars.
*   `POST /api/items`: Adds a new rental car. Expects a JSON body with `make`, `model`, `year`, and `price_per_day`. `available` defaults to `true`.
*   `GET /api/items/<item_id>`: Returns a specific car by its ID.
*   `PUT /api/items/<item_id>`: Updates an existing car. Expects a JSON body with fields to update (e.g., `make`, `model`, `year`, `price_per_day`, `available`).
*   `DELETE /api/items/<item_id>`: Deletes a specific car by its ID.
