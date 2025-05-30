from sqlalchemy.sql import func
from flask_login import UserMixin
from models import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'customer' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        print(f"[DEBUG] Setting password for user {self.email}")
        print(f"[DEBUG] Raw password: {password}")
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        print(f"[DEBUG] Generated hash: {hashed}")
        self.password_hash = hashed
        print(f"[DEBUG] Password hash set to: {self.password_hash}")

    def verify_password(self, password):
        print(f"[DEBUG] Verifying password for user {self.email}")
        print(f"[DEBUG] Stored hash: {self.password_hash}")
        print(f"[DEBUG] Password to verify: {password}")
        result = bcrypt.check_password_hash(self.password_hash, password)
        print(f"[DEBUG] Password verification result: {result}")
        return result

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def get_id(self):
        return str(self.id)
        
    @property
    def is_admin(self):
        return self.role == 'admin'
