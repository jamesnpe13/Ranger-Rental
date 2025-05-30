from app import create_app
from models import db, User

def check_admin_user():
    app = create_app()
    with app.app_context():
        # Check if the admin user exists
        admin = User.query.filter_by(email='admin@rangerental.com').first()
        if admin:
            print("Admin user found:")
            print(f"ID: {admin.id}")
            print(f"Email: {admin.email}")
            print(f"First Name: {admin.first_name}")
            print(f"Last Name: {admin.last_name}")
            print(f"Role: {admin.role}")
            print(f"Is Active: {admin.is_active}")
            print(f"Password Hash: {admin.password_hash}")
            
            # Verify the password
            print("\nVerifying password:")
            print(f"Verify 'admin123': {admin.verify_password('admin123')}")
            print(f"Verify 'wrong': {admin.verify_password('wrong')}")
        else:
            print("Admin user not found in the database")

if __name__ == '__main__':
    check_admin_user()
