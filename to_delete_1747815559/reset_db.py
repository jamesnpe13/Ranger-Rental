import os
from flask import Flask
from models import db, bcrypt, User
from sqlalchemy import text

def reset_database():
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///test.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='dev-key-change-in-production'
    )
    
    # Initialize extensions
    db.init_app(app)
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all tables")
        
        # Create all tables
        db.create_all()
        print("Created all tables")
        
        # Create admin user with direct password hashing
        password_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
        
        # Use direct SQL to insert the admin user
        db.session.execute(
            text("""
                INSERT INTO users (email, password_hash, first_name, last_name, role, is_active)
                VALUES (:email, :password_hash, :first_name, :last_name, :role, :is_active)
            """),
            {
                'email': 'admin@rangerental.com',
                'password_hash': password_hash,
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_active': True
            }
        )
        db.session.commit()
        print("Created admin user with direct SQL")
        
        # Verify the user was created
        result = db.session.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {'email': 'admin@rangerental.com'}
        ).fetchone()
        
        if result:
            user_data = dict(zip(['id', 'email', 'password_hash', 'first_name', 'last_name', 'role', 'is_active', 'created_at', 'updated_at'], result))
            print(f"Admin user created with ID: {user_data['id']}")
            print(f"Email: {user_data['email']}")
            print(f"Password hash: {user_data['password_hash']}")
            
            # Verify the password
            is_valid = bcrypt.check_password_hash(user_data['password_hash'], 'admin123')
            print(f"Password 'admin123' is valid: {is_valid}")
        else:
            print("Failed to create admin user")

if __name__ == '__main__':
    reset_database()
