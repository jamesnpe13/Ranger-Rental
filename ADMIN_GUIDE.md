# Admin Dashboard Guide

This guide provides instructions for setting up and using the admin dashboard for the Ranger-Rental application.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- All Python dependencies installed (from requirements.txt)

## Setup Instructions

### 1. Database Setup

1. Create a PostgreSQL database for the application
2. Update the database configuration in `config.py` with your database credentials

### 2. Create Admin User

Run the following command to create an admin user:

```bash
# Navigate to the backend directory
cd backend

# Create an admin user (interactive mode)
python create_admin.py

# Or with email and password as arguments
python create_admin.py admin@example.com your_secure_password
```

### 3. Start the Application

```bash
# Start the Flask development server
flask run

# Or with auto-reload for development
flask run --debug
```

The admin dashboard will be available at: http://localhost:5000/admin/

## Using the Admin Dashboard

### Login

1. Navigate to http://localhost:5000/admin/login
2. Enter your admin email and password
3. Click "Login"

### User Management

#### Viewing Users
- All users are displayed in a sortable and searchable table
- Use the search box to find specific users
- Click on column headers to sort

#### Adding a New User
1. Click the "Add New User" button
2. Fill in the user details:
   - First Name
   - Last Name
   - Email
   - Password
   - Role (Admin or User)
3. Click "Save User"

#### Editing a User
1. Click the edit (pencil) icon next to the user
2. Update the user details as needed
3. Click "Update User"

#### Deleting a User
1. Click the delete (trash) icon next to the user
2. Confirm the deletion in the dialog

#### Toggling User Status
- Click the status badge (Active/Inactive) to toggle a user's status
- Inactive users cannot log in

## Security Considerations

1. **Admin Access**: Only users with the 'admin' role can access the admin dashboard
2. **Password Security**:
   - Passwords are never stored in plaintext
   - All passwords are hashed using bcrypt
   - Minimum password length is 8 characters
3. **Session Security**:
   - Sessions are protected against CSRF attacks
   - Session cookies are marked as HttpOnly and Secure in production

## Troubleshooting

### Common Issues

1. **Login Fails**
   - Verify the email and password are correct
   - Check that the user has the 'admin' role
   - Ensure the user account is active

2. **Database Connection Issues**
   - Verify database credentials in `config.py`
   - Ensure the database server is running
   - Check database logs for connection errors

3. **Permissions Issues**
   - Ensure the database user has proper permissions
   - Check file permissions for the database file (if using SQLite)

## API Endpoints

The admin dashboard uses the following API endpoints:

- `GET /admin/api/users` - List all users
- `GET /admin/api/users/<id>` - Get a specific user
- `POST /admin/api/users` - Create a new user
- `PUT /admin/api/users/<id>` - Update a user
- `DELETE /admin/api/users/<id>` - Delete a user
- `POST /admin/api/users/<id>/status` - Toggle user status

## Support

For additional help, please contact the development team or refer to the project documentation.
