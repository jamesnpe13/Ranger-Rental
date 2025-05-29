from app import create_app
from models import User, db, bcrypt

def reset_admin_login():
    app = create_app()
    with app.app_context():
        print("\n=== RESETTING ADMIN LOGIN ===")
        
        # Delete existing admin users to avoid duplicates
        User.query.filter(User.email.in_(['admin@example.com', 'admin@admin.com'])).delete()
        db.session.commit()
        
        # Create a new admin user
        admin = User(
            email='admin@admin.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        
        # Set password
        password = 'admin1234'
        print(f"Setting password for admin@admin.com to: {password}")
        
        # Hash the password using bcrypt directly
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"Generated hash: {password_hash}")
        
        # Set the password hash directly
        admin.password_hash = password_hash
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        # Verify the user was created
        user = User.query.filter_by(email='admin@admin.com').first()
        if user:
            print("\n✅ Admin user created/updated successfully!")
            print(f"Email: {user.email}")
            print(f"Password: {password}")
            print(f"Password hash: {user.password_hash}")
            
            # Verify password
            is_valid = bcrypt.check_password_hash(user.password_hash, password)
            print(f"Password verification: {'✅ Success' if is_valid else '❌ Failed'}")
        else:
            print("❌ Failed to create admin user")

if __name__ == '__main__':
    reset_admin_login()
