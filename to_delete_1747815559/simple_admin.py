import traceback
import os
import sys
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template_string, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user, logout_user, login_user, UserMixin
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize blueprint
bp = Blueprint('simple_admin', __name__, url_prefix='/admin')

# Import db from the main app to avoid circular imports
from app import db

# Define a simple User class for admin purposes
class AdminUser(UserMixin):
    def __init__(self, id, email, role='admin'):
        self.id = id
        self.email = email
        self.role = role
        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

# Hardcoded admin user for MVP
ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASSWORD = 'admin1234'
ADMIN_USER = AdminUser(id=1, email=ADMIN_EMAIL)

# Simple user loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    if user_id == '1':
        return ADMIN_USER
    return None

bp = Blueprint('simple_admin', __name__, url_prefix='/admin')

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .login-container { max-width: 400px; margin: 100px auto; }
    </style>
</head>
<body>
    <div class="container login-container">
        <div class="card">
            <div class="card-header">
                <h4 class="mb-0">Admin Login</h4>
            </div>
            <div class="card-body">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                <form method="POST" action="{{ url_for('simple_admin.login') }}" id="login-form">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                    <input type="hidden" name="next" value="{{ request.args.get('next', '') }}">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" value="admin@admin.com" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" value="admin1234" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                <script>
                    // Prevent form resubmission on refresh
                    if (window.history.replaceState) {
                        window.history.replaceState(null, null, window.location.href);
                    }
                </script>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Base template that other templates will extend
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Admin Dashboard{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .sidebar {
            min-height: calc(100vh - 56px);
            background-color: #f8f9fa;
            padding: 20px 0;
        }
        .sidebar .nav-link {
            color: #333;
            padding: 10px 20px;
        }
        .sidebar .nav-link.active {
            background-color: #0d6efd;
            color: white;
        }
        .sidebar .nav-link:hover {
            background-color: #e9ecef;
        }
        .content {
            padding: 20px;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('simple_admin.dashboard') }}">RangerRental Admin</a>
            <div class="d-flex">
                <span class="navbar-text me-3 text-white">
                    {{ current_user.email }}
                </span>
                <a class="btn btn-outline-light btn-sm" href="{{ url_for('simple_admin.logout') }}">
                    Logout
                </a>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar">
                <div class="list-group list-group-flush">
                    <a href="{{ url_for('simple_admin.dashboard') }}" 
                       class="list-group-item list-group-item-action {% if request.endpoint == 'simple_admin.dashboard' %}active{% endif %}">
                        Dashboard
                    </a>
                    <a href="{{ url_for('simple_admin.vehicles') }}" 
                       class="list-group-item list-group-item-action {% if request.endpoint == 'simple_admin.vehicles' %}active{% endif %}">
                        Vehicles
                    </a>
                    <a href="{{ url_for('simple_admin.bookings') }}" 
                       class="list-group-item list-group-item-action {% if request.endpoint == 'simple_admin.bookings' %}active{% endif %}">
                        Bookings
                    </a>
                    <a href="{{ url_for('simple_admin.users') }}" 
                       class="list-group-item list-group-item-action {% if request.endpoint == 'simple_admin.users' %}active{% endif %}">
                        Users
                    </a>
                    <a href="{{ url_for('simple_admin.reports') }}" 
                       class="list-group-item list-group-item-action {% if request.endpoint == 'simple_admin.reports' %}active{% endif %}">
                        Reports
                    </a>
                </div>
            </div>
            
            <!-- Main content -->
            <div class="col-md-10 content">
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Dashboard template
DASHBOARD_TEMPLATE = BASE_TEMPLATE + """
{% block title %}Admin Dashboard - Overview{% endblock %}

{% block content %}
<div class="container-fluid">
    <!-- Page Header -->
    <div class="d-sm-flex align-items-center justify-content-between mb-4">
        <h1 class="h3 mb-0 text-gray-800">Dashboard</h1>
        <a href="{{ url_for('simple_admin.bookings') }}" class="d-none d-sm-inline-block btn btn-sm btn-primary shadow-sm">
            <i class="fas fa-calendar fa-sm text-white-50"></i> View All Bookings
        </a>
    </div>

    <!-- Stats Cards -->
    <div class="row">
        <!-- Total Users -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-primary shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                Total Users</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.users }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-users fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Total Vehicles -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-success shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                                Total Vehicles</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.vehicles }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-car fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Active Bookings -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-info shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                                Active Bookings</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">{{ stats.active_bookings }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-clipboard-list fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Total Revenue -->
        <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-warning shadow h-100 py-2">
                <div class="card-body">
                    <div class="row no-gutters align-items-center">
                        <div class="col mr-2">
                            <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                                Total Revenue</div>
                            <div class="h5 mb-0 font-weight-bold text-gray-800">${{ "%.2f"|format(stats.total_revenue) }}</div>
                        </div>
                        <div class="col-auto">
                            <i class="fas fa-dollar-sign fa-2x text-gray-300"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Content Row -->
    <div class="row">
        <!-- Recent Bookings -->
        <div class="col-lg-8 mb-4">
            <div class="card shadow mb-4">
                <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                    <h6 class="m-0 font-weight-bold text-primary">Recent Bookings</h6>
                    <div class="dropdown no-arrow">
                        <a class="dropdown-toggle" href="#" role="button" id="dropdownMenuLink"
                            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <i class="fas fa-ellipsis-v fa-sm fa-fw text-gray-400"></i>
                        </a>
                        <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in"
                            aria-labelledby="dropdownMenuLink">
                            <div class="dropdown-header">Booking Actions:</div>
                            <a class="dropdown-item" href="#">View All</a>
                            <a class="dropdown-item" href="#">Export</a>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-bordered" width="100%" cellspacing="0">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Vehicle</th>
                                    <th>Customer</th>
                                    <th>Dates</th>
                                    <th>Total</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for booking in recent_bookings %}
                                <tr>
                                    <td>#{{ booking.id }}</td>
                                    <td>{{ booking.vehicle.make }} {{ booking.vehicle.model }}</td>
                                    <td>{{ booking.user.email }}</td>
                                    <td>{{ booking.start_date.strftime('%b %d') }} - {{ booking.end_date.strftime('%b %d, %Y') }}</td>
                                    <td>${{ "%.2f"|format(booking.total_price) }}</td>
                                    <td>
                                        <span class="badge badge-{{ 'success' if booking.status == 'completed' else 'warning' }}">
                                            {{ booking.status|title }}
                                        </span>
                                    </td>
                                </tr>
                                {% else %}
                                <tr>
                                    <td colspan="6" class="text-center">No recent bookings</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Available Vehicles -->
        <div class="col-lg-4 mb-4">
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Available Vehicles</h6>
                </div>
                <div class="card-body">
                    {% for vehicle in available_vehicles %}
                    <div class="card mb-3 border-left-{{ 'success' if vehicle.is_available else 'secondary' }}">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col mr-2">
                                    <div class="text-xs font-weight-bold text-uppercase mb-1">
                                        {{ vehicle.make }} {{ vehicle.model }}
                                    </div>
                                    <div class="h6 mb-0 text-gray-800">
                                        ${{ "%.2f"|format(vehicle.price_per_day) }}/day
                                    </div>
                                    <div class="text-xs text-muted">
                                        {{ vehicle.type|title }} • {{ vehicle.seats }} seats
                                    </div>
                                </div>
                                <div class="col-auto">
                                    <i class="fas fa-car fa-2x text-gray-300"></i>
                                </div>
                            </div>
                        </div>
                        <div class="card-footer bg-transparent border-0">
                            <a href="#" class="btn btn-sm btn-primary">View Details</a>
                        </div>
                    </div>
                    {% else %}
                    <div class="text-center py-4">
                        <i class="fas fa-car fa-3x text-gray-300 mb-3"></i>
                        <p class="text-muted">No available vehicles</p>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card shadow mb-4">
                <div class="card-header py-3">
                    <h6 class="m-0 font-weight-bold text-primary">Quick Actions</h6>
                </div>
                <div class="card-body">
                    <a href="{{ url_for('simple_admin.add_vehicle') }}" class="btn btn-success btn-icon-split mb-3">
                        <span class="icon text-white-50">
                            <i class="fas fa-plus"></i>
                        </span>
                        <span class="text">Add New Vehicle</span>
                    </a>
                    <a href="#" class="btn btn-info btn-icon-split mb-3">
                        <span class="icon text-white-50">
                            <i class="fas fa-file-import"></i>
                        </span>
                        <span class="text">Import Bookings</span>
                    </a>
                    <a href="#" class="btn btn-warning btn-icon-split">
                        <span class="icon text-white-50">
                            <i class="fas fa-download"></i>
                        </span>
                        <span class="text">Generate Reports</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("\n" + "-"*50)
        print("ADMIN_REQUIRED DECORATOR CHECK")
        print(f"Current user: {current_user}")
        print(f"Is authenticated: {current_user.is_authenticated}")
        print(f"User role: {getattr(current_user, 'role', 'no role')}")
        
        if not current_user.is_authenticated:
            print("User not authenticated, redirecting to login")
            return redirect(url_for('simple_admin.login', next=request.url))
            
        if current_user.role != 'admin':
            print(f"User {current_user.email} is not an admin, access denied")
            flash('Admin access required', 'danger')
            return redirect(url_for('simple_admin.login'))
            
        print("Admin access granted")
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
def admin_root():
    # Redirect to dashboard if logged in, otherwise to login
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('simple_admin.dashboard'))
    return redirect(url_for('simple_admin.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        print("\n=== Login Route Accessed ===")
        print(f"Request method: {request.method}")
        print(f"Form data: {request.form}")
        
        # Handle form submission
        if request.method == 'POST':
            try:
                email = request.form.get('email')
                password = request.form.get('password')
                print(f"Login attempt - Email: {email}")
                
                # Simple hardcoded check for MVP
                if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                    print("Admin credentials verified")
                    try:
                        print(f"Logging in user: {ADMIN_EMAIL}")
                        login_user(ADMIN_USER)
                        print("User logged in, redirecting to dashboard")
                        return redirect(url_for('simple_admin.dashboard'))
                    except Exception as e:
                        print(f"Error during login: {str(e)}")
                        print(traceback.format_exc())
                        error_msg = "Error during login"
                else:
                    print("Invalid credentials")
                    error_msg = "Invalid email or password"
                    
            except Exception as e:
                print(f"Error during login: {str(e)}")
                print(traceback.format_exc())
                error_msg = "An error occurred during login"
        else:
            error_msg = ""
    except Exception as e:
        print(f"Unexpected error in login route: {str(e)}")
        print(traceback.format_exc())
        error_msg = "An unexpected error occurred"
    
    # Simple login form
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background: #f8f9fa; }}
            .login-container {{ margin-top: 100px; }}
            .error {{ color: red; margin-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-4">
                    <div class="card login-container">
                        <div class="card-header bg-primary text-white">
                            <h4 class="mb-0">Admin Login</h4>
                        </div>
                        <div class="card-body">
                            {'<div class="alert alert-danger">' + error_msg + '</div>' if error_msg else ''}
                            <form method="POST" action="/admin/login">
                                <div class="mb-3">
                                    <label for="email" class="form-label">Email</label>
                                    <input type="email" class="form-control" id="email" name="email" value="admin@admin.com" required>
                                </div>
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" value="admin1234" required>
                                </div>
                                <button type="submit" class="btn btn-primary w-100">Login</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    if request.method == 'POST':
        try:
            print("\n" + "-"*50)
            print("LOGIN ATTEMPT")
            print(f"Content-Type: {request.content_type}")
            print(f"Form data: {request.form}")
            print(f"JSON data: {request.get_json(silent=True) or 'No JSON data'}")
            
            # Handle both form data and JSON data
            if request.is_json:
                data = request.get_json()
                email = data.get('email')
                password = data.get('password')
            else:
                email = request.form.get('email')
                password = request.form.get('password')
                
            print(f"Login attempt - Email: {email}, Password: {'*' * len(password) if password else 'None'}")
            
            if not email or not password:
                flash('Please enter both email and password', 'error')
                return redirect(url_for('simple_admin.login'))
            
            # Debug: Print all users in the database
            from models import User
            all_users = User.query.all()
            print("\nALL USERS IN DATABASE:")
            for u in all_users:
                print(f"- {u.email} (ID: {u.id}, Role: {u.role}, Active: {u.is_active})")
            
            user = User.query.filter_by(email=email).first()
            print(f"\nFOUND USER: {user}")
            
            if not user:
                print(f"No user found with email: {email}")
                flash('Invalid email or password', 'error')
                return redirect(url_for('simple_admin.login'))
                
            print(f"User found - ID: {user.id}, Email: {user.email}, Role: {user.role}, Active: {user.is_active}")
            print(f"Password hash: {user.password_hash[:30]}...")
            
            if not user.is_active:
                print("User account is not active")
                flash('This account is not active', 'error')
                return redirect(url_for('simple_admin.login'))
                
            # Debug password verification
            print("\n=== PASSWORD VERIFICATION DEBUG ===")
            print(f"Password to verify: {password}")
            print(f"Stored hash: {user.password_hash}")
            
            # Check password with bcrypt directly
            import bcrypt
            password_bytes = password.encode('utf-8')
            hash_bytes = user.password_hash.encode('utf-8')
            print(f"BCrypt check: {bcrypt.checkpw(password_bytes, hash_bytes)}")
            
            # Check with verify_password
            verify_result = user.verify_password(password)
            print(f"verify_password result: {verify_result}")
            
            if not verify_result:
                print("Password verification failed")
                flash('Invalid email or password', 'error')
                return redirect(url_for('simple_admin.login'))
                
            # If we get here, login is successful
            print("Password verified successfully!")
            login_user(user)
            
            if request.is_json:
                return {'message': 'Login successful', 'redirect': url_for('simple_admin.dashboard')}
                
            next_page = request.args.get('next') or url_for('simple_admin.dashboard')
            print(f"Login successful, redirecting to: {next_page}")
            return redirect(next_page)
            
        except Exception as e:
            print(f"Error during login: {str(e)}")
            print(traceback.format_exc())
            
            if request.is_json:
                return {'message': 'An error occurred during login. Please try again.'}, 500
                
            flash('An error occurred during login. Please try again.', 'error')
            return render_template_string(LOGIN_TEMPLATE)
    
    # If it's a GET request, show the login form
    try:
        return render_template_string(LOGIN_TEMPLATE)
    except Exception as e:
        print(f"Error rendering login template: {str(e)}")
        print(traceback.format_exc())
        return "An error occurred while loading the login page. Please check the server logs.", 500

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    try:
        print("\n" + "="*80)
        print("DASHBOARD ROUTE - START")
        print(f"Current user: {current_user}")
        print(f"User ID: {getattr(current_user, 'id', 'N/A')}")
        print(f"User email: {getattr(current_user, 'email', 'N/A')}")
        print(f"Is authenticated: {current_user.is_authenticated}")
        print(f"User role: {getattr(current_user, 'role', 'no role')}")
        print(f"Request method: {request.method}")
        print(f"Request URL: {request.url}")
        print(f"Session: {dict(session)}")
        print(f"Headers: {dict(request.headers)}")
        
        # Initialize stats with default values
        stats = {
            'users': 0,
            'vehicles': 0,
            'active_bookings': 0,
            'total_revenue': 0,
            'recent_bookings': [],
            'available_vehicles': []
        }
        
        try:
            # Test database connection
            from models import db
            db.session.execute('SELECT 1')
            print("✅ Database connection test successful")
            
            # Get user count
            try:
                stats['users'] = User.query.count()
                print(f"✅ Users counted: {stats['users']}")
            except Exception as e:
                print(f"❌ Error counting users: {str(e)}")
                print(traceback.format_exc())
            
            # Get vehicle count
            try:
                stats['vehicles'] = Vehicle.query.count()
                print(f"✅ Vehicles counted: {stats['vehicles']}")
            except Exception as e:
                print(f"❌ Error counting vehicles: {str(e)}")
                print(traceback.format_exc())
            
            # Get active bookings
            try:
                stats['active_bookings'] = Booking.query.filter(
                    Booking.status.in_(['confirmed', 'in_progress'])
                ).count()
                print(f"✅ Active bookings: {stats['active_bookings']}")
            except Exception as e:
                print(f"❌ Error counting active bookings: {str(e)}")
                print(traceback.format_exc())
            
            # Calculate total revenue
            try:
                completed_bookings = Booking.query.filter_by(status='completed').all()
                print(f"✅ Found {len(completed_bookings)} completed bookings")
                stats['total_revenue'] = sum(
                    float(booking.total_price) 
                    for booking in completed_bookings
                    if booking and hasattr(booking, 'total_price') and booking.total_price
                )
                print(f"✅ Total revenue: ${stats['total_revenue']:.2f}")
            except Exception as e:
                print(f"❌ Error calculating revenue: {str(e)}")
                print(traceback.format_exc())
            
            # Get recent bookings
            try:
                stats['recent_bookings'] = Booking.query.order_by(
                    Booking.created_at.desc()
                ).limit(5).all()
                print(f"✅ Found {len(stats['recent_bookings'])} recent bookings")
            except Exception as e:
                print(f"❌ Error fetching recent bookings: {str(e)}")
                print(traceback.format_exc())
            
            # Get available vehicles
            try:
                stats['available_vehicles'] = Vehicle.query.filter_by(
                    status='available'
                ).limit(5).all()
                print(f"✅ Found {len(stats['available_vehicles'])} available vehicles")
            except Exception as e:
                print(f"❌ Error fetching available vehicles: {str(e)}")
                print(traceback.format_exc())
            
        except Exception as e:
            print(f"❌ Error in dashboard data collection: {str(e)}")
            print(traceback.format_exc())
        
        # Render the dashboard template
        try:
            print("\nRendering dashboard template...")
            return render_template_string(DASHBOARD_TEMPLATE, stats=stats)
        except Exception as e:
            print(f"❌ Error rendering template: {str(e)}")
            print(traceback.format_exc())
            raise
        
    except Exception as e:
        print("\n" + "!"*80)
        print(f"❌ FATAL ERROR in dashboard route: {str(e)}")
        print(traceback.format_exc())
        print("!"*80 + "\n")
        
        return jsonify({
            'success': False,
            'error': {
                'code': 'DASHBOARD_ERROR',
                'message': str(e),
                'type': type(e).__name__
            }
        }), 500
        available_vehicles = []
        try:
            print("Fetching available vehicles...")
            available_vehicles = Vehicle.query.filter_by(is_available=True).limit(5).all()
            print(f"Found {len(available_vehicles)} available vehicles")
        except Exception as e:
            print(f"Error getting available vehicles: {str(e)}")
            print(traceback.format_exc())
        
        # Render the template with all data
        print("Rendering template...")
        return render_template_string(
            DASHBOARD_TEMPLATE,
            stats=stats,
            recent_bookings=recent_bookings,
            available_vehicles=available_vehicles,
            now=datetime.utcnow()
        )
        
    except Exception as e:
        error_msg = f"""
        CRITICAL ERROR IN DASHBOARD:
        Type: {type(e).__name__}
        Message: {str(e)}
        Traceback:
        {traceback.format_exc()}
        """
        print("\n" + "="*70)
        print(error_msg)
        print("="*70 + "\n")
        
        # Return a simple error page
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - Admin Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .error-container {{ max-width: 800px; margin: 50px auto; }}
                .error-details {{ 
                    background-color: #f8d7da; 
                    border: 1px solid #f5c6cb;
                    border-radius: 5px;
                    padding: 15px;
                    margin-top: 20px;
                    white-space: pre-wrap;
                    font-family: monospace;
                    font-size: 14px;
                }}
                .action-links {{ margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container error-container">
                <div class="alert alert-danger">
                    <h4 class="alert-heading">Error Loading Dashboard</h4>
                    <p>An error occurred while loading the admin dashboard. Please try again later.</p>
                    <hr>
                    <p class="mb-0">If the problem persists, please contact support.</p>
                </div>
                <div class="error-details">
                    Error Type: {error_type}<br>
                    Error Message: {error_message}
                </div>
                <div class="action-links">
                    <a href="{dashboard_url}" class="btn btn-primary">Try Again</a>
                    <a href="{logout_url}" class="btn btn-outline-secondary ms-2">Logout</a>
                </div>
            </div>
        </body>
        </html>
        """.format(
            error_type=type(e).__name__,
            error_message=str(e),
            dashboard_url=url_for('simple_admin.dashboard'),
            logout_url=url_for('simple_admin.logout')
        )
        return error_html

@bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template_string("""
        <h1>Users</h1>
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Name</th>
                    <th>Role</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.id }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.first_name }} {{ user.last_name }}</td>
                    <td>{{ user.role }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <a href="{{ url_for('simple_admin.dashboard') }}" class="btn btn-secondary">Back to Dashboard</a>
    """, users=users)

@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('simple_admin.login'))
