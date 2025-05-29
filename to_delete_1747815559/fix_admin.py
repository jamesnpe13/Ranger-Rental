from app import create_app
from models import db, User

def fix_admin_user():
    app = create_app()
    with app.app_context():
        # Delete existing admin user if exists
        admin = User.query.filter_by(email='admin@rangerental.com').first()
        if admin:
            db.session.delete(admin)
            db.session.commit()
            print("Deleted existing admin user")
        
        # Create a new admin user with a known password
        new_admin = User(
            email='admin@rangerental.com',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True
        )
        # Set password directly using the setter
        new_admin.password = 'admin123'
        
        db.session.add(new_admin)
        db.session.commit()
        print("Created new admin user with email: admin@rangerental.com and password: admin123")
        
        # Verify the user was created
        verify_admin = User.query.filter_by(email='admin@rangerental.com').first()
        print(f"Verification - User exists: {verify_admin is not None}")
        if verify_admin:
            print(f"Password hash: {verify_admin.password_hash}")
            print(f"Verification test: {verify_admin.verify_password('admin123')}")

if __name__ == '__main__':
    fix_admin_user()
