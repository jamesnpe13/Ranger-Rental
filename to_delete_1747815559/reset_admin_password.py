from app import create_app
from models import db, User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        # Find the admin user
        admin = User.query.filter_by(email='admin@rangerental.com').first()
        if not admin:
            print("Admin user not found. Creating one...")
            admin = User(
                email='admin@rangerental.com',
                first_name='Admin',
                last_name='User',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
        else:
            print("Resetting admin password...")
            admin.password = 'admin123'  # This will be hashed by the setter
        
        db.session.commit()
        print("Admin password has been reset to 'admin123'")

if __name__ == '__main__':
    reset_admin_password()
