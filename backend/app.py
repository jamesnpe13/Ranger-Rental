import os
import logging
import sqlite3
from flask import Flask, request, jsonify, g
from flask_cors import CORS  # Import CORS
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)  # For password hashing
from admin_auth import verify_admin_credentials  # Import for admin auth

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)  # More explicit CORS config

# --- Logging Setup ---
# Determine log level from FLASK_DEBUG environment variable
DEBUG_MODE_LOGGING = os.environ.get("FLASK_DEBUG", "0").lower() in ["true", "1", "t"]
log_level = logging.DEBUG if DEBUG_MODE_LOGGING else logging.INFO

logging.basicConfig(
    level=log_level, format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)

app.logger.setLevel(log_level)  # Ensure Flask's logger also respects this level
# --- End Logging Setup ---

# --- Database Setup ---
DATABASE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ranger_rental.db"
)


def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER,
            price_per_day REAL NOT NULL,
            available BOOLEAN NOT NULL DEFAULT 1 CHECK (available IN (0, 1))
        )
    """
    )
    # Example: Add some initial data if the table is empty (optional)
    cursor.execute("SELECT COUNT(*) FROM cars")
    if cursor.fetchone()[0] == 0:
        app.logger.info("Database is empty, populating with initial car data.")
        initial_cars = [
            ("Toyota", "Camry", 2022, 50, 1),
            ("Honda", "Civic", 2021, 45, 0),
            ("Ford", "Mustang", 2023, 75, 1),
        ]
        cursor.executemany(
            "INSERT INTO cars (make, model, year, price_per_day, available) VALUES (?, ?, ?, ?, ?)",
            initial_cars,
        )
        app.logger.info(f"{len(initial_cars)} initial cars inserted.")

    # Create users table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'customer'))
        )
    """
    )
    app.logger.info("Users table checked/created.")

    # Seed initial users if the table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        app.logger.info(
            "Users table is empty, populating with initial admin and customer users."
        )
        initial_users = [
            (
                "admin",
                generate_password_hash("adminpass", method="pbkdf2:sha256"),
                "admin",
            ),
            (
                "customer1",
                generate_password_hash("customerpass", method="pbkdf2:sha256"),
                "customer",
            ),
        ]
        cursor.executemany(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            initial_users,
        )
        app.logger.info(f"{len(initial_users)} initial users inserted.")

    conn.commit()
    conn.close()
    app.logger.info("Database initialized successfully.")


# --- End Database Setup ---

# Global in-memory list for cars (replace with database in a real app)
# sample_items = [
#     {"id": 1, "make": "Toyota", "model": "Camry", "year": 2022, "price_per_day": 50, "available": True},
#     {"id": 2, "make": "Honda", "model": "Civic", "year": 2021, "price_per_day": 45, "available": False},
#     {"id": 3, "make": "Ford", "model": "Mustang", "year": 2023, "price_per_day": 75, "available": True},
#     {"id": 4, "make": "Chevrolet", "model": "Silverado", "year": 2022, "price_per_day": 80, "available": True},
#     {"id": 5, "make": "Nissan", "model": "Altima", "year": 2020, "price_per_day": 40, "available": True}
# ]


@app.route("/")
def home():
    return jsonify(message="Welcome to the Ranger-Rental API!")


# API endpoint to get all items or add a new item
@app.route("/api/items", methods=["GET", "POST"])
def handle_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "GET":
        cursor.execute("SELECT * FROM cars")
        cars = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(cars)

    elif request.method == "POST":
        new_car_data = request.get_json(silent=True)
        if new_car_data is None:
            conn.close()
            return (
                jsonify(
                    message="Request body must be valid JSON.",
                    error_code="INVALID_JSON_BODY",
                ),
                400,
            )

        required_fields = ["make", "model", "year", "price_per_day"]
        missing_fields = [
            field for field in required_fields if field not in new_car_data
        ]
        if missing_fields:
            conn.close()
            return (
                jsonify(
                    message=f"Missing required fields: {', '.join(missing_fields)}.",
                    error_code="MISSING_FIELDS",
                    details={"missing_fields": missing_fields},
                ),
                400,
            )

        make = new_car_data.get("make")
        model = new_car_data.get("model")
        year = new_car_data.get("year")
        price_per_day = new_car_data.get("price_per_day")
        available = new_car_data.get("available", True)

        errors = {}
        if not isinstance(make, str) or not make.strip():
            errors["make"] = "Must be a non-empty string"
        if not isinstance(model, str) or not model.strip():
            errors["model"] = "Must be a non-empty string"
        if not isinstance(year, int) or year < 1900 or year > 2030:
            errors["year"] = "Must be an integer between 1900 and 2030"
        if not isinstance(price_per_day, (int, float)) or price_per_day <= 0:
            errors["price_per_day"] = "Must be a positive number"
        if "available" in new_car_data and not isinstance(available, bool):
            errors["available"] = "Must be a boolean (true or false)"

        if errors:
            conn.close()
            return (
                jsonify(
                    message="Input validation failed. Please check the provided data.",
                    error_code="VALIDATION_ERROR",
                    errors=errors,
                ),
                400,
            )

        try:
            cursor.execute(
                "INSERT INTO cars (make, model, year, price_per_day, available) VALUES (?, ?, ?, ?, ?)",
                (
                    make.strip(),
                    model.strip(),
                    year,
                    price_per_day,
                    1 if available else 0,
                ),
            )
            conn.commit()
            new_car_id = cursor.lastrowid
            conn.close()

            # Fetch the newly created car to return it
            conn_fetch = get_db_connection()
            cursor_fetch = conn_fetch.cursor()
            cursor_fetch.execute("SELECT * FROM cars WHERE id = ?", (new_car_id,))
            created_car = dict(cursor_fetch.fetchone())
            conn_fetch.close()

            app.logger.info(
                f"New car added: ID {new_car_id}, Make: {created_car['make']}"
            )
            return jsonify(created_car), 201
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            app.logger.error(f"Database error on car creation: {e}")
            return (
                jsonify(
                    message="Database error during car creation.",
                    error_code="DATABASE_ERROR",
                    details=str(e),
                ),
                500,
            )


# --- User Authentication Endpoints ---
@app.route("/api/login", methods=["POST"])
def login():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json(silent=True)

    if not data or not data.get("username") or not data.get("password"):
        conn.close()
        return (
            jsonify(
                message="Username and password are required.",
                error_code="MISSING_CREDENTIALS",
            ),
            400,
        )

    username = data.get("username")
    password = data.get("password")

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_row = cursor.fetchone()
    conn.close()  # Close connection early as we have the data or know user doesn't exist

    if user_row:
        user = dict(user_row)
        if check_password_hash(user["password_hash"], password):
            app.logger.info(
                f"User '{username}' logged in successfully. Role: {user['role']}"
            )
            # For now, just return role. Later, we might implement session tokens.
            return (
                jsonify(
                    message="Login successful",
                    username=user["username"],
                    role=user["role"],
                ),
                200,
            )
        else:
            app.logger.warning(
                f"Failed login attempt for user '{username}': Incorrect password"
            )
            return (
                jsonify(
                    message="Invalid username or password",
                    error_code="INVALID_CREDENTIALS",
                ),
                401,
            )
    else:
        app.logger.warning(f"Failed login attempt: User '{username}' not found")
        return (
            jsonify(
                message="Invalid username or password", error_code="INVALID_CREDENTIALS"
            ),
            401,
        )


# --- Admin Login Endpoint ---
@app.route("/api/admin/login", methods=["POST"])
def admin_login_route():
    data = request.get_json(silent=True)
    if not data or not data.get("username") or not data.get("password"):
        return (
            jsonify(
                message="Username and password are required for admin login.",
                error_code="MISSING_CREDENTIALS",
            ),
            400,
        )

    username = data.get("username")
    password = data.get("password")

    if verify_admin_credentials(username, password):
        app.logger.info(f"Admin user '{username}' logged in successfully.")
        # In a real app, you'd establish a session here (e.g., Flask-Login, JWT tokens)
        return (
            jsonify(message="Admin login successful", username=username, role="admin"),
            200,
        )
    else:
        app.logger.warning(f"Failed admin login attempt for user '{username}'.")
        return (
            jsonify(
                message="Invalid admin username or password, or not an admin user.",
                error_code="ADMIN_INVALID_CREDENTIALS",
            ),
            401,
        )


@app.route("/api/admin/register", methods=["POST"])
def admin_register_route():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json(silent=True)

    if not data or not data.get("username") or not data.get("password"):
        conn.close()
        return (
            jsonify(
                message="Username and password are required for admin registration.",
                error_code="MISSING_CREDENTIALS",
            ),
            400,
        )

    username = data.get("username")
    password = data.get("password")
    # In a more secure setup, you might require an 'admin_code' from the request
    # and validate it here before proceeding.
    # admin_code = data.get('admin_code')
    # if not admin_code or admin_code != "YOUR_SECRET_ADMIN_REGISTRATION_CODE":
    #     conn.close()
    #     return jsonify(message="Invalid or missing admin registration code."), 403

    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return (
            jsonify(
                message=f"Username '{username}' already exists.",
                error_code="USERNAME_EXISTS",
            ),
            409,
        )  # 409 Conflict

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed_password, "admin"),
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        app.logger.info(
            f"New admin user '{username}' (ID: {user_id}) registered successfully."
        )
        return (
            jsonify(
                message="Admin user registered successfully",
                username=username,
                userId=user_id,
                role="admin",
            ),
            201,
        )
    except (
        sqlite3.IntegrityError
    ):  # Should be caught by the earlier check, but as a safeguard
        conn.rollback()
        conn.close()
        app.logger.warning(
            f"Failed to register admin user '{username}' due to integrity error (likely username exists)."
        )
        return (
            jsonify(
                message=f"Username '{username}' already exists.",
                error_code="USERNAME_EXISTS_DB_ERROR",
            ),
            409,
        )
    except sqlite3.Error as e:
        conn.rollback()
        conn.close()
        app.logger.error(
            f"Database error during admin registration for '{username}': {e}"
        )
        return (
            jsonify(
                message="Database error during admin registration.",
                error_code="DATABASE_ERROR",
                details=str(e),
            ),
            500,
        )


# --- Admin Vehicle Management ---
@app.route("/api/admin/vehicles", methods=["POST"])
def admin_add_vehicle():
    # TODO: Add admin authentication check here (e.g., check session/token)
    # For now, we assume if this endpoint is called, it's an authorized admin.
    # if not is_admin_user():
    #     return jsonify(message="Unauthorized: Admin access required."), 403

    data = request.get_json(silent=True)
    if not data:
        return (
            jsonify(
                message="Request body must be valid JSON.",
                error_code="INVALID_JSON_BODY",
            ),
            400,
        )

    required_fields = ["make", "model", "year", "price_per_day"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return (
            jsonify(
                message=f"Missing required fields: {', '.join(missing_fields)}.",
                error_code="MISSING_FIELDS",
                details={"missing_fields": missing_fields},
            ),
            400,
        )

    make = data.get("make")
    model = data.get("model")
    year = data.get("year")
    price_per_day = data.get("price_per_day")
    available = data.get("available", True)  # Default to True if not provided

    # Basic Validation
    errors = {}
    if not isinstance(make, str) or not make.strip():
        errors["make"] = "Must be a non-empty string"
    if not isinstance(model, str) or not model.strip():
        errors["model"] = "Must be a non-empty string"
    if not isinstance(year, int) or not (1900 <= year <= 2099):
        errors["year"] = "Must be an integer year (e.g., 1900-2099)"
    if not isinstance(price_per_day, (int, float)) or price_per_day <= 0:
        errors["price_per_day"] = "Must be a positive number"
    if "available" in data and not isinstance(available, bool):
        errors["available"] = "Must be a boolean (true or false)"

    if errors:
        return (
            jsonify(
                message="Input validation failed.",
                error_code="VALIDATION_ERROR",
                errors=errors,
            ),
            400,
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO cars (make, model, year, price_per_day, available) VALUES (?, ?, ?, ?, ?)",
            (make.strip(), model.strip(), year, price_per_day, 1 if available else 0),
        )
        conn.commit()
        new_car_id = cursor.lastrowid

        # Fetch the newly created car to return it
        cursor.execute("SELECT * FROM cars WHERE id = ?", (new_car_id,))
        created_car = dict(cursor.fetchone())

        app.logger.info(
            f"Admin added new vehicle: ID {new_car_id}, Make: {make}, Model: {model}"
        )
        return jsonify(message="Vehicle added successfully!", vehicle=created_car), 201
    except sqlite3.Error as e:
        conn.rollback()
        app.logger.error(f"Database error when admin adding vehicle: {e}")
        return (
            jsonify(
                message="Database error occurred while adding vehicle.",
                error_code="DATABASE_ERROR",
                details=str(e),
            ),
            500,
        )
    finally:
        conn.close()


@app.route("/api/register", methods=["POST"])
def register():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json(silent=True)

    if not data or not data.get("username") or not data.get("password"):
        conn.close()
        return (
            jsonify(
                message="Username and password are required.",
                error_code="MISSING_CREDENTIALS",
            ),
            400,
        )

    username = data.get("username")
    password = data.get("password")
    role = "customer"  # Default role for new registrations

    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        app.logger.warning(
            f"Registration attempt failed: Username '{username}' already exists."
        )
        return (
            jsonify(
                message="Username already exists. Please choose a different one.",
                error_code="USERNAME_EXISTS",
            ),
            409,
        )  # 409 Conflict

    try:
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hashed_password, role),
        )
        conn.commit()
        app.logger.info(f"New user '{username}' registered successfully as '{role}'.")
        return jsonify(message="Registration successful. You can now login."), 201
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error during registration for '{username}': {e}")
        return (
            jsonify(
                message="An error occurred during registration. Please try again.",
                error_code="REGISTRATION_ERROR",
            ),
            500,
        )
    finally:
        conn.close()


# API endpoint to get, update, or delete a single item by its ID
@app.route("/api/items/<int:item_id>", methods=["GET", "PUT", "DELETE"])
def handle_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cars WHERE id = ?", (item_id,))
    car_row = cursor.fetchone()

    if car_row is None:
        conn.close()
        return (
            jsonify(
                message=f"Car with ID {item_id} not found.", error_code="NOT_FOUND"
            ),
            404,
        )

    car = dict(car_row)  # Convert to dict for easier manipulation if needed for PUT

    if request.method == "GET":
        conn.close()
        return jsonify(car)

    elif request.method == "PUT":
        update_data = request.get_json(silent=True)
        if update_data is None:
            conn.close()
            return (
                jsonify(
                    message="Request body must be valid JSON and cannot be empty.",
                    error_code="INVALID_JSON_BODY",
                ),
                400,
            )

        # Fields to update
        updated_make = update_data.get("make", car["make"])
        updated_model = update_data.get("model", car["model"])
        updated_year = update_data.get("year", car["year"])
        updated_price = update_data.get("price_per_day", car["price_per_day"])
        updated_available = update_data.get(
            "available", car["available"] == 1
        )  # Convert db 0/1 to bool

        errors = {}
        if "make" in update_data and (
            not isinstance(updated_make, str) or not updated_make.strip()
        ):
            errors["make"] = "Must be a non-empty string"
        if "model" in update_data and (
            not isinstance(updated_model, str) or not updated_model.strip()
        ):
            errors["model"] = "Must be a non-empty string"
        if "year" in update_data and (
            not isinstance(updated_year, int)
            or updated_year < 1900
            or updated_year > 2030
        ):
            errors["year"] = "Must be an integer between 1900 and 2030"
        if "price_per_day" in update_data and (
            not isinstance(updated_price, (int, float)) or updated_price <= 0
        ):
            errors["price_per_day"] = "Must be a positive number"
        if "available" in update_data and not isinstance(updated_available, bool):
            errors["available"] = "Must be a boolean (true or false)"

        if errors:
            conn.close()
            return (
                jsonify(
                    message="Input validation failed. Please check the provided data.",
                    error_code="VALIDATION_ERROR",
                    errors=errors,
                ),
                400,
            )

        try:
            cursor.execute(
                "UPDATE cars SET make = ?, model = ?, year = ?, price_per_day = ?, available = ? WHERE id = ?",
                (
                    (
                        updated_make.strip()
                        if isinstance(updated_make, str)
                        else updated_make
                    ),
                    (
                        updated_model.strip()
                        if isinstance(updated_model, str)
                        else updated_model
                    ),
                    updated_year,
                    updated_price,
                    1 if updated_available else 0,
                    item_id,
                ),
            )
            conn.commit()
            conn.close()

            # Fetch the updated car to return it
            conn_fetch = get_db_connection()
            cursor_fetch = conn_fetch.cursor()
            cursor_fetch.execute("SELECT * FROM cars WHERE id = ?", (item_id,))
            updated_car_data = dict(cursor_fetch.fetchone())
            conn_fetch.close()

            app.logger.info(f"Car ID {item_id} updated.")
            return jsonify(updated_car_data)
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            app.logger.error(f"Database error on car update for ID {item_id}: {e}")
            return (
                jsonify(
                    message="Database error during car update.",
                    error_code="DATABASE_ERROR",
                    details=str(e),
                ),
                500,
            )

    elif request.method == "DELETE":
        try:
            cursor.execute("DELETE FROM cars WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            app.logger.info(f"Car ID {item_id} deleted.")
            # Return the original car data (before deletion) as part of the response
            return jsonify(
                message=f"Car with ID {item_id} deleted successfully.", deleted_item=car
            )
        except sqlite3.Error as e:
            conn.rollback()
            conn.close()
            app.logger.error(f"Database error on car deletion for ID {item_id}: {e}")
            return (
                jsonify(
                    message="Database error during car deletion.",
                    error_code="DATABASE_ERROR",
                    details=str(e),
                ),
                500,
            )


@app.before_request
def log_request_info():
    app.logger.debug(
        f"Request: {request.method} {request.path} from {request.remote_addr}"
    )
    app.logger.debug(f"Headers: {request.headers}")
    if request.data:
        app.logger.debug(f"Body: {request.get_data(as_text=True)}")


@app.after_request
def log_response_info(response):
    app.logger.debug(f"Response: {response.status} {response.get_data(as_text=True)}")
    return response


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    app.logger.error(
        f"An unexpected error occurred: {e}", exc_info=True
    )  # exc_info=True logs stack trace
    return (
        jsonify(
            message="An unexpected internal server error occurred.",
            error_code="INTERNAL_SERVER_ERROR",
        ),
        500,
    )


if __name__ == "__main__":
    # Configuration from environment variables
    # FLASK_DEBUG=1 or true for debug mode, 0 or false for production (default: 0)
    DEBUG_MODE = os.environ.get("FLASK_DEBUG", "0").lower() in ["true", "1", "t"]
    # Default host to 127.0.0.1 (localhost), set to 0.0.0.0 for external access
    HOST = os.environ.get("APP_HOST", "127.0.0.1")
    # Default port to 5000
    PORT = int(os.environ.get("APP_PORT", 5000))

    app.logger.info(f"Starting Ranger-Rental API server...")
    app.logger.info(
        f' * Environment: {"production" if not DEBUG_MODE else "development"}'
    )
    app.logger.info(f" * Debug mode: {DEBUG_MODE}")
    app.logger.info(f" * Running on http://{HOST}:{PORT}/")

    # Werkzeug logger can be noisy, set its level higher if desired, especially in production
    # logging.getLogger('werkzeug').setLevel(logging.WARNING)

    init_db()  # Initialize the database and table
    app.run(host=HOST, port=PORT, debug=DEBUG_MODE, use_reloader=DEBUG_MODE)
