from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

# Initialize the app
app = create_app()

with app.app_context():
    # Find the admin user
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if admin:
        # Update the password
        new_password = 'admin123'  # Set your desired password here
        admin.password = generate_password_hash(new_password, method='sha256')
        admin.is_active = True
        db.session.commit()
        print(f"✅ Admin password has been reset to: {new_password}")
    else:
        print("❌ Admin user not found. Creating a new admin user...")
        # Create a new admin user
        from create_admin import create_admin
        create_admin('admin@example.com', 'admin123')
        print("✅ New admin user created with email: admin@example.com and password: admin123")
