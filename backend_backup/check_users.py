from app import create_app
from models import db, User

def check_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the database.")
            # Create admin user if not exists
            admin = User(
                email='admin@rangerental.com',
                first_name='Admin',
                last_name='User',
                password='admin123',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Created admin user.")
        else:
            print("Users in database:")
            for user in users:
                print(f"ID: {user.id}, Email: {user.email}, Name: {user.first_name} {user.last_name}, Role: {user.role}")

if __name__ == '__main__':
    check_users()
