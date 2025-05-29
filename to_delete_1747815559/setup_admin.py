from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True
            )
            admin.password = 'admin123'  # Change this to a secure password
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print(f"Email: admin@example.com")
            print(f"Password: admin123")
            print("\n⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("ℹ️  Admin user already exists")
            print(f"Email: {admin.email}")
            print("If you forgot the password, you can reset it in the database.")

if __name__ == '__main__':
    create_admin_user()
