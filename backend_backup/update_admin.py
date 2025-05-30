from app import create_app
from models import User, db
from werkzeug.security import generate_password_hash

def update_admin_password():
    app = create_app()
    with app.app_context():
        # Get the admin user
        user = User.query.filter_by(email='admin@example.com').first()
        if not user:
            print("Admin user not found!")
            return
            
        # Update the password
        user.password_hash = generate_password_hash('admin1234', method='pbkdf2:sha256')
        db.session.commit()
        print("Admin password has been updated to 'admin1234'")
        print(f"Email: {user.email}")
        print(f"Password: admin1234")

if __name__ == '__main__':
    update_admin_password()
