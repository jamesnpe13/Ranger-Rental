from app import create_app
from models import db, User

def init_db():
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create default admin user
        if not User.query.filter_by(email='admin@rangerental.com').first():
            admin = User(
                email='admin@rangerental.com',
                first_name='Admin',
                last_name='User',
                password='admin123',  # In production, use a secure password
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Database initialized with admin user")

if __name__ == '__main__':
    init_db()
