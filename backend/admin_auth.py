
import sqlite3
from werkzeug.security import check_password_hash
# Assuming app.py is in the same directory and provides get_db_connection
# If app.py is structured as a module or blueprint, imports might need adjustment.
# For simplicity, we might need to duplicate get_db_connection or pass db_path

DATABASE_FILE = 'ranger_rental.db' # Path to your database file

def get_db_connection_for_auth(): # Renamed to avoid potential conflict if imported elsewhere
    """Helper function to get a database connection."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def verify_admin_credentials(username, password):
    """
    Verify admin credentials against the database.
    Checks if the user exists, the password is correct, and the user has the 'admin' role.
    """
    conn = None # Initialize conn to None
    try:
        conn = get_db_connection_for_auth()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()

        if user_row:
            user = dict(user_row) # Convert sqlite3.Row to dict
            # Check password and role
            if check_password_hash(user['password_hash'], password) and user['role'] == 'admin':
                return True
        return False
    except sqlite3.Error as e:
        # Log this error in a real application
        print(f"Database error during admin verification: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Example usage (can be removed or kept for direct testing)
if __name__ == '__main__':
    # This assumes you have seeded an admin user as per your app.py (e.g., admin/adminpass)
    # For this test to work, ensure DATABASE_FILE points correctly relative to this script
    # or provide an absolute path.
    print("Testing admin_auth.py (ensure database is initialized with an admin user)...")
    
    # Test with correct admin credentials (replace with your actual seeded admin)
    # Assuming an admin user 'admin' with password 'adminpass' exists from app.py init_db
    if verify_admin_credentials("admin", "adminpass"):
        print("Admin login with correct credentials: SUCCESS")
    else:
        print("Admin login with correct credentials: FAILED")

    # Test with incorrect password
    if not verify_admin_credentials("admin", "wrongpassword"):
        print("Admin login with incorrect password: SUCCESS (should fail)")
    else:
        print("Admin login with incorrect password: FAILED (should succeed at failing)")

    # Test with non-admin user (assuming 'customer1' with 'customerpass' exists)
    if not verify_admin_credentials("customer1", "customerpass"):
        print("Login attempt with non-admin user: SUCCESS (should fail as admin)")
    else:
        print("Login attempt with non-admin user: FAILED (should succeed at failing as admin)")

    # Test with non-existent user
    if not verify_admin_credentials("nouser", "anypass"):
        print("Login attempt with non-existent user: SUCCESS (should fail)")
    else:
        print("Login attempt with non-existent user: FAILED (should succeed at failing)")

