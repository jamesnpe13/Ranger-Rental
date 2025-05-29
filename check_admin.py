from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    # Check if any admin users exist
    admin_users = User.query.filter_by(role='admin').all()
    
    if not admin_users:
        print("No admin users found in the database!")
    else:
        print(f"Found {len(admin_users)} admin user(s):")
        for user in admin_users:
            print(f"- ID: {user.id}, Email: {user.email}, Active: {user.is_active}")
    
    # Check if the default admin user exists
    default_admin = User.query.filter_by(email='admin@admin.com').first()
    if not default_admin:
        print("\nDefault admin user (admin@admin.com) not found!")
    else:
        print(f"\nDefault admin user found:")
        print(f"- ID: {default_admin.id}")
        print(f"- Email: {default_admin.email}")
        print(f"- Role: {default_admin.role}")
        print(f"- Active: {default_admin.is_active}")
