# Ranger Rentals - MVP Backend

This is the minimal viable product (MVP) backend for the Ranger Rentals application.

## Project Structure

```
backend/
├── api/                   # API endpoints
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   └── payments.py        # Payment processing
├── models/                # Database models
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── vehicle.py         # Vehicle model
│   ├── booking.py         # Booking model
│   └── payment.py         # Payment model
├── app.py                # Application factory
├── requirements.txt      # Project dependencies
└── run.py               # Application entry point
```

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python run.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user profile

### Payments
- `POST /api/payments` - Create a new payment
- `GET /api/payments/<payment_id>` - Get payment details
- `GET /api/payments/booking/<booking_id>` - Get payments for a booking
