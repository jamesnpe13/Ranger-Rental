# Ranger-Rental API Backend

# Ranger-Rental API Backend

This backend provides a RESTful API for managing car rentals for the Ranger-Rental application. It uses Flask for the web framework and SQLite for data persistence.

## Features

*   List all rental cars.
*   Add a new rental car.
*   View details of a specific car.
*   Update an existing car's information.
*   Delete a car from the inventory.
*   Input validation for all create and update operations.
*   Consistent JSON error responses.
*   Configurable via environment variables (debug mode, host, port).
*   Logging for requests, responses, and errors.
*   Data is stored in a SQLite database file (`backend/ranger_rental.db`) which is created automatically.

## Setup and Running

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**
    ```bash
    python app.py
    ```

The application will start, and a `ranger_rental.db` file will be created in the `backend` directory to store the car data if it doesn't already exist. The API will be available at `http://<host>:<port>` (default `http://127.0.0.1:5000`).

### Configuration (Environment Variables)

Before running, you can set the following environment variables to configure the application:

*   `FLASK_DEBUG`: Set to `1` or `true` to enable Flask debug mode. Defaults to `0` (disabled).
    *   Example: `export FLASK_DEBUG=1`
*   `APP_HOST`: The host address the server will listen on. Defaults to `127.0.0.1` (localhost). Set to `0.0.0.0` to listen on all available network interfaces.
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
