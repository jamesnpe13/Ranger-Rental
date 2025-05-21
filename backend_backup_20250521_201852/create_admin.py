import sys
import getpass
from app import create_app, db
from models.user import User
from models import bcrypt

def create_admin(email='admin@admin.com', password='admin123', first_name='Admin', last_name='User'):
    """Create an admin user with default credentials"""
    app = create_app()
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Update existing user to admin
            if existing_user.role != 'admin':
                existing_user.role = 'admin'
                existing_user.is_active = True
                db.session.commit()
                print(f"\n✅ Existing user updated to admin!")
            else:
                print(f"\nℹ️  User {email} is already an admin.")
            return
            
        # Create new admin user
        admin = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='admin',
            is_active=True
        )
        admin.set_password(password)  # This will hash the password
        
        db.session.add(admin)
        db.session.commit()
        print(f"\n✅ Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")

if __name__ == '__main__':
    try:
        print("=== Admin User Creation ===\n")
        
        # If no arguments provided, use defaults
        if len(sys.argv) == 1:
            create_admin()  # Use default credentials
            sys.exit(0)
            
        # Get email and password from command line or prompt
        if len(sys.argv) > 2:
            email = sys.argv[1]
            password = sys.argv[2]
            create_admin(email, password)
        else:
            print("Enter admin user details (or press Ctrl+C to cancel):")
            email = input("Email [admin@admin.com]: ").strip() or 'admin@admin.com'
            while True:
                password = getpass.getpass("Password (min 8 characters): ").strip()
                if len(password) >= 8:
                    break
                print("Password must be at least 8 characters long")
        
        # Confirm before creating
        print(f"\nWill create admin user with:")
        print(f"Email: {email}")
        print(f"Password: {'*' * len(password)}")
        
        if len(sys.argv) <= 2:  # Only confirm if not running from command line with args
            confirm = input("\nCreate this admin user? [y/N]: ").strip().lower()
            if confirm != 'y':
                print("\nOperation cancelled.")
                sys.exit(0)
        
        # Create the admin user
        create_admin(email, password)
        
        # Print success message with next steps
        print("\n✅ Admin user created successfully!")
        print("\nYou can now log in to the admin dashboard at:")
        print("http://localhost:5000/admin/")
        print("\nNote: Make sure the Flask application is running with the correct database configuration.")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error creating admin user: {str(e)}")
        sys.exit(1)
