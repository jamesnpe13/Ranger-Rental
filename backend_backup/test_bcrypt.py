from flask import Flask
from flask_bcrypt import Bcrypt
from models import db, User

def test_bcrypt():
    # Create a test Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    bcrypt = Bcrypt(app)
    db.init_app(app)
    
    with app.app_context():
        # Test 1: Direct bcrypt hashing and verification
        print("\n=== Test 1: Direct bcrypt hashing and verification ===")
        password = 'admin123'
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Password: {password}")
        print(f"Hashed: {hashed}")
        print(f"Verification: {bcrypt.check_password_hash(hashed, password)}")
        
        # Test 2: Check the stored hash in the database
        print("\n=== Test 2: Check stored hash in database ===")
        user = User.query.filter_by(email='admin@rangerental.com').first()
        if user:
            print(f"Found user: {user.email}")
            print(f"Stored hash: {user.password_hash}")
            print(f"Verification with bcrypt: {bcrypt.check_password_hash(user.password_hash, 'admin123')}")
            print(f"Verification with user method: {user.verify_password('admin123')}")
        else:
            print("Admin user not found in database")
        
        # Test 3: Create a new user and verify
        print("\n=== Test 3: Create new user and verify ===")
        try:
            new_user = User(
                email='test@example.com',
                first_name='Test',
                last_name='User',
                password='test123',
                role='customer'
            )
            db.session.add(new_user)
            db.session.commit()
            print("Created new user")
            print(f"New user hash: {new_user.password_hash}")
            print(f"Verification: {bcrypt.check_password_hash(new_user.password_hash, 'test123')}")
            print(f"Verification with wrong password: {bcrypt.check_password_hash(new_user.password_hash, 'wrong')}")
            
            # Clean up
            db.session.delete(new_user)
            db.session.commit()
            print("Cleaned up test user")
        except Exception as e:
            print(f"Error creating test user: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    test_bcrypt()
