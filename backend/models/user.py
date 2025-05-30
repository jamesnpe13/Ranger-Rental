from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from datetime import datetime

class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.Text, nullable=False)  # Using Text type to ensure no length limitations
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    payments = db.relationship('Payment', backref='user', lazy=True)

    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.set_password(password)

    def set_password(self, password):
        """Create hashed password with consistent settings."""
        self.password = generate_password_hash(
            password,
            method='pbkdf2:sha256:600000',
            salt_length=16
        )
        print(f"New password hash: {self.password}")

    def check_password(self, password):
        """Check hashed password with error handling."""
        try:
            # Direct comparison first
            if check_password_hash(self.password, password):
                return True
                
            # If that fails, try to fix common formatting issues
            hash_parts = self.password.split('$')
            if len(hash_parts) >= 3:
                # Reconstruct the hash in the format: method$salt$hash
                reconstructed_hash = f"{hash_parts[0]}${hash_parts[1]}${hash_parts[2]}"
                if check_password_hash(reconstructed_hash, password):
                    # Update the hash to the correct format
                    self.password = reconstructed_hash
                    return True
                    
            # If we get here, all checks failed
            print(f"Password check failed for user {self.email}")
            return False
            
        except Exception as e:
            print(f"Password check error: {e}")
            return False

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.username}>'
