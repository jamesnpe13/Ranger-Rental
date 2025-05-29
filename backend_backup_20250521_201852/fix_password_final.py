from app import create_app
from models import User, db

def fix_admin_password():
    app = create_app()
    with app.app_context():
        # Get or create the admin user
        user = User.query.filter_by(email='admin@example.com').first()
        if not user:
            print("Admin user not found! Creating one...")
            user = User(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True
            )
            db.session.add(user)
        
        # Set the password
        user.password = 'admin1234'
        db.session.commit()
        
        # Verify the user exists and can be authenticated
        user = User.query.filter_by(email='admin@example.com').first()
        if user and user.verify_password('admin1234'):
            print("✅ Admin user is ready to use!")
            print(f"Email: {user.email}")
            print(f"Password: admin1234")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
        else:
            print("❌ Failed to set up admin user!")

if __name__ == '__main__':
    fix_admin_password()
