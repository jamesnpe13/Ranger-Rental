from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    app = create_app()
    with app.app_context():
        # Get the admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            print("❌ Admin user not found!")
            return
            
        # Set new password
        new_password = 'admin123'  # You can change this to your preferred password
        admin.password_hash = generate_password_hash(new_password)
        admin.is_active = True
        db.session.commit()
        
        print("✅ Admin password has been reset!")
        print(f"Email: {admin.email}")
        print(f"New password: {new_password}")
        print("\nYou can now log in at: http://localhost:5000/admin/")

if __name__ == '__main__':
    reset_admin_password()
