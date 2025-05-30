from app import create_app
from models import db, bcrypt
from models.user import User

app = create_app()

with app.app_context():
    # Create all database tables
    print("Creating database tables...")
    db.create_all()
    
    # Check if admin user exists
    admin_email = "admin@example.com"
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        print("Creating admin user...")
        admin = User(
            email=admin_email,
            password="admin123",  # Change this in production!
            first_name="Admin",
            last_name="User",
            role="admin",
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin user: {admin_email}")
    else:
        print(f"Admin user already exists: {admin_email}")
    
    print("Database check complete.")
    print(f"Total users in database: {User.query.count()}")
