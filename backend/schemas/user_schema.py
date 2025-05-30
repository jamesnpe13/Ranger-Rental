from marshmallow import Schema, fields, validate, validates, ValidationError
from models.user import User

class UserSchema(Schema):
    """Schema for user data validation and serialization."""
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    password = fields.Str(load_only=True, required=True, validate=validate.Length(min=6))
    is_admin = fields.Bool(dump_only=True)
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('email')
    def validate_email(self, value):
        """Validate that email is not already registered."""
        if User.query.filter_by(email=value).first():
            raise ValidationError('Email already registered')

    class Meta:
        fields = ('id', 'email', 'first_name', 'last_name', 'is_admin', 'is_active', 'created_at', 'updated_at')
        ordered = True
