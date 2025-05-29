from flask import Flask
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, text

def test_auth():
    # Initialize Flask app and bcrypt
    app = Flask(__name__)
    bcrypt = Bcrypt(app)
    
    # Database connection
    engine = create_engine('sqlite:///instance/test.db')
    
    # Get the stored hash
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT password_hash FROM users WHERE email = :email"),
            {'email': 'admin@rangerental.com'}
        ).fetchone()
        
        if not result:
            print("User not found")
            return
            
        stored_hash = result[0]
        print(f"Stored hash: {stored_hash}")
        
        # Test password verification
        password = 'admin123'
        is_valid = bcrypt.check_password_hash(stored_hash, password)
        print(f"Password 'admin123' is valid: {is_valid}")
        
        # Generate a new hash for the same password
        new_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Newly generated hash: {new_hash}")
        print(f"New hash matches stored hash: {new_hash == stored_hash}")
        print(f"New hash verification: {bcrypt.check_password_hash(new_hash, password)}")

if __name__ == '__main__':
    test_auth()
