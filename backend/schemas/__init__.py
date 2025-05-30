"""
Data validation schemas using Marshmallow.
"""
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    """Schema for user data validation."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)

# Export the UserSchema
__all__ = ['UserSchema']

class VehicleSchema(Schema):
    """Schema for vehicle data validation."""
    make = fields.Str(required=True)
    model = fields.Str(required=True)
    year = fields.Int(required=True, validate=validate.Range(min=1900, max=2100))
    type = fields.Str(required=True)
    price_per_day = fields.Float(required=True, validate=validate.Range(min=0))
    location = fields.Str(required=True)
    description = fields.Str()

class BookingSchema(Schema):
    """Schema for booking data validation."""
    vehicle_id = fields.Int(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
