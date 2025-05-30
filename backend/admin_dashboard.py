from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app, session
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from models import db, bcrypt
from models.user import User
from models.vehicle import Vehicle
from models.booking import Booking
from functools import wraps
from datetime import datetime, timedelta
import os
import json
import logging
import sys
import secrets
from flask import flash, get_flashed_messages

# Initialize the blueprint with template and static folders
bp = Blueprint('admin_ui',  # Changed from 'admin' to 'admin_ui' to avoid conflicts
              __name__, 
              url_prefix='/admin',
              template_folder=os.path.abspath('../../frontend/admin'),
              static_folder=os.path.abspath('../../frontend/static'))

# Test route to verify session and authentication
@bp.route('/test-auth')
def test_auth():
    """Test route to verify session and authentication"""
    output = [
        "=== Test Authentication ===",
        f"Python version: {sys.version}",
        f"Flask session: {dict(session)}",
        f"Current user: {current_user}",
        f"Is authenticated: {current_user.is_authenticated}",
        f"User role: {getattr(current_user, 'role', 'N/A')}",
        f"Session ID: {session.get('_id', 'No session ID')}",
        f"Session data: {dict(session)}",
        f"Cookies: {request.cookies}",
    ]
    return '<br>'.join(output)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("\n=== Admin Required Decorator ===")
        print(f"Current user: {current_user.email if hasattr(current_user, 'email') else 'Not authenticated'}")
        print(f"User role: {getattr(current_user, 'role', 'No role')}")
        print(f"Session data: {dict(session)}")
        print(f"Request endpoint: {request.endpoint}")
        
        # Check if user is authenticated
        if not current_user.is_authenticated:
            print("User not authenticated, redirecting to login")
            return redirect(url_for('admin_ui.login', next=request.url))
        
        # Check if user is admin
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            print("User is not an admin, showing error")
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('admin_ui.login', next=request.url))
        
        # If we get here, user is authenticated and is an admin
        print("User is authenticated and is an admin, proceeding...")
        return f(*args, **kwargs)
    return decorated_function

# Login manager setup
def init_login_manager(login_manager):
    login_manager.login_view = 'admin_ui.login'  # Updated to use admin_ui blueprint
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            print(f"\n=== Loading user with ID: {user_id} ===")
            
            # Check if this is a fresh session (not coming from a cleared session)
            if '_fresh' not in session or not session['_fresh']:
                print("Session is not fresh, forcing logout")
                return None
                
            user = User.query.get(int(user_id))
            if user:
                print(f"User loaded: {user}")
                print(f"User role: {getattr(user, 'role', 'No role')}")
                # Set session as not fresh for the next request
                session['_fresh'] = False
                return user
            return None
        except Exception as e:
            print(f"Error in load_user: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

# Login route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Generate CSRF token if it doesn't exist
    if '_csrf_token' not in session:
        session['_csrf_token'] = os.urandom(24).hex()
    csrf_token = session['_csrf_token']
    
    # Get next page from query parameters or form data
    next_page = request.args.get('next') or request.form.get('next', '')
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        try:
            # Verify CSRF token
            form_csrf = request.form.get('csrf_token')
            if not csrf_token or not form_csrf or not secrets.compare_digest(csrf_token, form_csrf):
                flash('Invalid request. Please try again.', 'error')
                return redirect(url_for('admin_ui.login', next=next_page))
            
            # Get form data
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            print(f"Login attempt for email: {email}")
            
            if not email or not password:
                flash('Email and password are required', 'error')
                return redirect(url_for('admin_ui.login', next=next_page))
            
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if user and user.role == 'admin' and user.check_password(password):
                print(f"Login successful for user: {email}")
                
                # Clear any existing session data for security
                session.clear()
                
                # Login the user
                login_user(user, remember=False)
                
                # Set session variables
                session['_user_id'] = user.id
                session['_fresh'] = True
                
                # Ensure next_page is a relative URL for security
                if not next_page.startswith('/'):
                    next_page = url_for('admin_ui.dashboard')
                
                print(f"Redirecting to: {next_page}")
                response = redirect(next_page)
                
                # Add security headers
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                
                return response
            else:
                print(f"Login failed for email: {email}")
                flash('Invalid email or password', 'error')
                return redirect(url_for('admin_ui.login', next=next_page))
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('An error occurred during login. Please try again.', 'error')
            return redirect(url_for('admin_ui.login', next=next_page))
    
    # Handle GET request (show login form)
    from_logout = request.args.get('from_logout') == '1'
    
    # If coming from logout, clear the session completely
    if from_logout:
        session.clear()
        session['_fresh'] = False
    
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role == 'admin':
        return redirect(url_for('admin_ui.dashboard'))
    
    # Debug info
    print("\n=== Login Form Display ===")
    print(f"Current user: {current_user}")
    print(f"Is authenticated: {current_user.is_authenticated}")
    print(f"Next page: {next_page}")
    
    # Render the login form
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{
                background-color: #f8f9fa;
            }}
            .login-container {{
                max-width: 400px;
                margin: 100px auto;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .form-group {{
                margin-bottom: 1rem;
            }}
            .alert {{
                margin-bottom: 1rem;
                padding: 0.75rem 1.25rem;
                border: 1px solid transparent;
                border-radius: 0.25rem;
            }}
            .alert-error {{
                color: #721c24;
                background-color: #f8d7da;
                border-color: #f5c6cb;
            }}
            .alert-success {{
                color: #155724;
                background-color: #d4edda;
                border-color: #c3e6cb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="login-container">
                <h2 class="text-center mb-4">Admin Login</h2>
                
                {get_flashed_messages_html()}
                
                <form method="POST" action="{url_for('admin_ui.login')}">
                    <input type="hidden" name="csrf_token" value="{csrf_token}">
                    <input type="hidden" name="next" value="{next_page}">
                    
                    <div class="form-group">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" 
                               class="form-control" 
                               id="email" 
                               name="email" 
                               value="admin@admin.com" 
                               required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" 
                               class="form-control" 
                               id="password" 
                               name="password" 
                               value="admin1234" 
                               required>
                    </div>
                    
                    <div class="d-grid gap-2 mt-4">
                        <button type="submit" class="btn btn-primary">
                            Sign In
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """

def get_flashed_messages_html():
    """Helper function to format flash messages as HTML"""
    messages = get_flashed_messages(with_categories=True)
    if not messages:
        return ""
    
    html_parts = []
    for category, message in messages:
        # Map Flask's message categories to Bootstrap alert classes
        alert_class = {
            'error': 'danger',
            'message': 'info',
            'success': 'success',
            'warning': 'warning',
        }.get(category, 'info')
        
        html_parts.append(f'''
        <div class="alert alert-{alert_class} alert-dismissible fade show" role="alert">
            {message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>''')
    
    return '\n'.join(html_parts)

# Admin root route - redirects to login or dashboard based on auth status
@bp.route('/')
def admin_root():
    try:
        print("\n=== Admin Root ===")
        print(f"Current user: {current_user}")
        print(f"Is authenticated: {current_user.is_authenticated}")
        
        # If user is already authenticated and is an admin, go to dashboard
        if current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role == 'admin':
            print("User is already authenticated, redirecting to dashboard")
            return redirect(url_for('admin_ui.dashboard'))
        
        # Otherwise, redirect to login
        print("User not authenticated, redirecting to login")
        response = redirect(url_for('admin_ui.login'))
        
        # Clear any existing session cookies
        response.delete_cookie('session', path='/')
        response.delete_cookie('session', path='/admin')
        
        # Add security headers
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
        
    except Exception as e:
        print(f"Error in admin_root: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # If anything fails, do a simple redirect to login
        return redirect(url_for('admin_ui.login'))

# Dashboard route
@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    print("\n=== Dashboard Access ===")
    print(f"Current user: {current_user.email}")
    print(f"User role: {current_user.role}")
    print(f"Session: {dict(session)}")
    
    try:
        # Get counts for dashboard
        user_count = User.query.count()
        vehicle_count = Vehicle.query.count()
        booking_count = Booking.query.count()
        
        # Get recent bookings
        recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
        
        return render_template('dashboard.html',
                             user_count=user_count,
                             vehicle_count=vehicle_count,
                             booking_count=booking_count,
                             recent_bookings=recent_bookings)
    except Exception as e:
        print(f"Error rendering dashboard: {str(e)}")
        flash('Error loading dashboard. Please try again.', 'error')
        return redirect(url_for('admin_ui.admin_root')), 500

# Check session endpoint
@bp.route('/api/check-session')
def check_session():
    """Check if the current session is authenticated"""
    try:
        if current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role == 'admin':
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': current_user.id,
                    'email': current_user.email,
                    'role': current_user.role
                }
            })
        return jsonify({'authenticated': False}), 401
    except Exception as e:
        print(f"Error checking session: {str(e)}")
        return jsonify({'authenticated': False, 'error': str(e)}), 500

# API: List all users
@bp.route('/api/users', methods=['GET'])
@login_required
@admin_required
def api_list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        'users': [{
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None
        } for user in users]
    })

# API: Get single user
@bp.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def api_get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'updated_at': user.updated_at.isoformat() if user.updated_at else None
    })

# API: Create user
@bp.route('/api/users', methods=['POST'])
@login_required
@admin_required
def api_create_user():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate role
    if data['role'] not in ['admin', 'customer']:
        return jsonify({'error': 'Invalid role. Must be either "admin" or "customer"'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    try:
        user = User(
            email=data['email'],
            password=data['password'],  # Password will be hashed by the model's setter
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'],
            is_active=data.get('is_active', True)
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error creating user: {str(e)}')
        return jsonify({'error': 'Failed to create user. Please try again.'}), 500

# API: Update user
@bp.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if 'email' in data and data['email'] != user.email:
            if User.query.filter(User.email == data['email'], User.id != user_id).first():
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'password' in data and data['password']:
            user.password = data['password']
        
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating user {user_id}: {str(e)}')
        return jsonify({'error': 'Failed to update user. Please try again.'}), 500

# API: Delete user
@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 403
    
    user = User.query.get_or_404(user_id)
    
    try:
        # Check for existing bookings before deleting
        from models.booking import Booking
        has_bookings = Booking.query.filter_by(user_id=user_id).first() is not None
        
        if has_bookings:
            # Instead of deleting, deactivate the user
            user.is_active = False
            db.session.commit()
            return jsonify({
                'message': 'User has existing bookings. Account has been deactivated instead of deleted.',
                'user_id': user.id,
                'is_active': False
            }), 200
        else:
            db.session.delete(user)
            db.session.commit()
            return '', 204
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting user {user_id}: {str(e)}')
        return jsonify({'error': 'Failed to delete user. Please try again.'}), 500

# API: Toggle user status
@bp.route('/api/users/<int:user_id>/status', methods=['POST'])
@login_required
@admin_required
def api_toggle_user_status(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot modify your own account'}), 403
    
    user = User.query.get_or_404(user_id)
    
    try:
        data = request.get_json() or {}
        new_status = data.get('is_active', not user.is_active)
        
        # Prevent deactivating the last admin
        if user.role == 'admin' and not new_status:
            admin_count = User.query.filter_by(role='admin', is_active=True).count()
            if admin_count <= 1:
                return jsonify({
                    'error': 'Cannot deactivate the last active admin account. '
                            'Please assign another admin first.'
                }), 400
        
        user.is_active = new_status
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'is_active': user.is_active,
            'message': f'User has been {"activated" if user.is_active else "deactivated"}'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error toggling status for user {user_id}: {str(e)}')
        return jsonify({'error': 'Failed to update user status. Please try again.'}), 500

# Logout route
@bp.route('/logout', methods=['GET'])
def logout():
    try:
        print("\n=== Logging out user ===")
        print(f"Current user before logout: {current_user}")
        
        # Get the current user ID before logging out
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Clear all session data first
        session.clear()
        
        # Log out the user if they're logged in
        if current_user.is_authenticated:
            logout_user()
            print("User logged out successfully")
        
        # Create a response that will clear all session data
        response = redirect(url_for('admin_ui.login', from_logout=1, _external=True))
        
        # Clear all possible cookies
        cookie_names = [
            'session', 'remember_token', 'session_id', 'flask',
            'session_', 'csrftoken', 'auth_token', 'token'
        ]
        
        # Clear cookies for all paths and subdomains
        paths = ['/', '/admin']
        domains = [None, request.host.split(':', 1)[0]]  # Current domain only
        
        for domain in domains:
            for path in paths:
                for name in cookie_names:
                    response.set_cookie(
                        key=name,
                        value='',
                        expires=0,
                        path=path,
                        domain=domain,
                        secure=request.is_secure,
                        httponly=True,
                        samesite='Lax'
                    )
        
        # Add security headers to prevent caching and protect against various attacks
        security_headers = {
            'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0, private',
            'Pragma': 'no-cache',
            'Expires': '0',
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Clear-Site-Data': '"cache", "cookies", "storage"',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        print("Session and cookies cleared, redirecting to login")
        return response
        
    except Exception as e:
        print(f"Error during logout: {str(e)}")
        import traceback
        traceback.print_exc()
        # If anything fails, do a hard redirect with URL parameters
        login_url = f"{url_for('admin_ui.login', _external=True)}?from_logout=1&cleared=1"
        response = redirect(login_url)
        
        # Clear cookies in case of error too
        response.delete_cookie('session', path='/')
        response.delete_cookie('session', path='/admin')
        response.delete_cookie('remember_token', path='/')
        response.delete_cookie('remember_token', path='/admin')
        
        return response

# Users Management
@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    
    # Build query
    query = User.query
    
    # Apply search filter
    if search:
        search = f"%{search}%"
        query = query.filter(
            (User.first_name.ilike(search)) |
            (User.last_name.ilike(search)) |
            (User.email.ilike(search))
        )
    
    # Get paginated results
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', 
                         users=pagination.items,
                         pagination=pagination,
                         search=request.args.get('search', ''))

# Vehicle Management
@bp.route('/vehicles')
@login_required
@admin_required
def vehicles():
    """
    Display and manage vehicles in the admin panel.
    Supports pagination, searching, and filtering.
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', 'all')
        
        # Log access
        current_app.logger.info(
            f"Vehicles page accessed by {current_user.email} - "
            f"Page: {page}, Search: '{search}', Status: {status}"
        )
        
        # Build base query
        query = Vehicle.query
        
        # Apply search filter if provided
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                or_(
                    Vehicle.make.ilike(search_term),
                    Vehicle.model.ilike(search_term),
                    Vehicle.license_plate.ilike(search_term),
                    Vehicle.vin.ilike(search_term)
                )
            )
        
        # Apply status filter
        if status != 'all':
            if status == 'available':
                query = query.filter(Vehicle.is_available == True)
            elif status == 'unavailable':
                query = query.filter(Vehicle.is_available == False)
        
        # Execute query with pagination
        vehicles_pagination = query.order_by(Vehicle.created_at.desc()).paginate(
            page=page, 
            per_page=min(per_page, 100),  # Limit max per_page to 100 for performance
            error_out=False
        )
        
        # Get vehicle status counts for the filter
        total_vehicles = Vehicle.query.count()
        available_count = Vehicle.query.filter_by(is_available=True).count()
        
        return render_template('vehicles.html',
                             vehicles=vehicles_pagination.items,
                             pagination=vehicles_pagination,
                             search=search,
                             status=status,
                             total_vehicles=total_vehicles,
                             available_count=available_count,
                             current_year=datetime.now().year)
                             
    except Exception as e:
        current_app.logger.error(f"Error in vehicles route: {str(e)}", exc_info=True)
        flash('An error occurred while loading vehicles. Please try again later.', 'error')
        return redirect(url_for('admin_ui.dashboard'))

# Booking Management
@bp.route('/bookings')
@login_required
@admin_required
def bookings():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search = request.args.get('search', '')
    
    # Build query with joins to get user and vehicle info
    query = db.session.query(Booking).join(User).join(Vehicle)
    
    # Apply search filter
    if search:
        search = f"%{search}%"
        query = query.filter(
            (User.first_name.ilike(search)) |
            (User.last_name.ilike(search)) |
            (User.email.ilike(search)) |
            (Vehicle.make.ilike(search)) |
            (Vehicle.model.ilike(search)) |
            (Booking.status.ilike(search))
        )
    
    # Get paginated results
    pagination = query.order_by(Booking.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
@bp.route('/api/vehicles', methods=['GET'])
@login_required
@admin_required
def api_list_vehicles():
    """
    Enhanced API endpoint to list vehicles with:
    - Advanced search across multiple fields
    - Multiple filter options
    - Sorting
    - Pagination
    """
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 items per page
        
        # Initialize query
        query = Vehicle.query
        
        # Apply search filter
        search = request.args.get('search', '').strip()
        if search:
            search = f"%{search}%"
            query = query.filter(
                or_(
                    Vehicle.make.ilike(search),
                    Vehicle.model.ilike(search),
                    Vehicle.registration_number.ilike(search),
                    Vehicle.vehicle_type.ilike(search),
                    Vehicle.description.ilike(search)
                )
            )
        
        # Apply filters
        if 'status' in request.args:
            status = request.args.get('status')
            if status == 'available':
                query = query.filter(Vehicle.is_available == True)
            elif status == 'unavailable':
                query = query.filter(Vehicle.is_available == False)
        
        if 'make' in request.args:
            query = query.filter(Vehicle.make.ilike(f"%{request.args.get('make')}%"))
            
        if 'vehicle_type' in request.args:
            query = query.filter(Vehicle.vehicle_type.ilike(f"%{request.args.get('vehicle_type')}%"))
            
        if 'min_price' in request.args:
            query = query.filter(Vehicle.price_per_day >= float(request.args.get('min_price')))
            
        if 'max_price' in request.args:
            query = query.filter(Vehicle.price_per_day <= float(request.args.get('max_price')))
        
        # Apply sorting
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if hasattr(Vehicle, sort_by):
            sort_field = getattr(Vehicle, sort_by)
            if sort_order.lower() == 'asc':
                query = query.order_by(sort_field.asc())
            else:
                query = query.order_by(sort_field.desc())
        
        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get distinct values for filters
        makes = [m[0] for m in db.session.query(Vehicle.make).distinct().all() if m[0]]
        types = [t[0] for t in db.session.query(Vehicle.vehicle_type).distinct().all() if t[0]]
        
        # Prepare response
        vehicles = [{
            'id': v.id,
            'make': v.make,
            'model': v.model,
            'year': v.year,
            'vehicle_type': v.vehicle_type,
            'registration_number': v.registration_number,
            'price_per_day': float(v.price_per_day) if v.price_per_day else None,
            'is_available': v.is_available,
            'mileage': v.mileage,
            'seats': v.seats,
            'doors': v.doors,
            'transmission': v.transmission,
            'fuel_type': v.fuel_type,
            'created_at': v.created_at.isoformat() if v.created_at else None,
            'updated_at': v.updated_at.isoformat() if v.updated_at else None
        } for v in pagination.items]
        
        return jsonify({
            'success': True,
            'data': {
                'vehicles': vehicles,
                'filters': {
                    'makes': sorted(makes),
                    'types': sorted(types),
                    'min_price': db.session.query(db.func.min(Vehicle.price_per_day)).scalar() or 0,
                    'max_price': db.session.query(db.func.max(Vehicle.price_per_day)).scalar() or 1000
                }
            },
            'pagination': {
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching vehicles: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Failed to fetch vehicles: {str(e)}'
        }), 500

# API: Save or update vehicle with enhanced validation and error handling
@bp.route('/api/vehicles', methods=['POST'])
@bp.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
@login_required
@admin_required
def api_save_vehicle(vehicle_id=None):
    """
    Handle vehicle creation and updates with:
    - Comprehensive validation
    - Better error messages
    - Image handling
    - Audit logging
    """
    try:
        # Check if request is JSON or form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            
        # Enhanced validation
        validation_errors = []
        
        # Required fields validation
        required_fields = {
            'make': 'Make is required',
            'model': 'Model is required',
            'year': 'Year is required',
            'registration_number': 'Registration number is required',
            'price_per_day': 'Price per day is required',
            'vehicle_type': 'Vehicle type is required'
        }
        
        for field, error_msg in required_fields.items():
            if field not in data or not str(data[field]).strip():
                validation_errors.append(error_msg)
        
        # Numeric validation
        numeric_fields = {
            'year': ('Year', 1900, datetime.now().year + 1),
            'price_per_day': ('Price per day', 0, 10000),
            'mileage': ('Mileage', 0, 1000000),
            'seats': ('Seats', 1, 100),
            'doors': ('Doors', 1, 10)
        }
        
        for field, (label, min_val, max_val) in numeric_fields.items():
            if field in data and data[field]:
                try:
                    num_val = float(data[field])
                    if not (min_val <= num_val <= max_val):
                        validation_errors.append(f"{label} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    validation_errors.append(f"{label} must be a valid number")
        
        # Check for duplicate registration number
        if 'registration_number' in data and data['registration_number']:
            existing = Vehicle.query.filter(
                Vehicle.registration_number == data['registration_number'].strip(),
                Vehicle.id != vehicle_id if vehicle_id else True
            ).first()
            
            if existing:
                validation_errors.append('A vehicle with this registration number already exists')
        
        if validation_errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': validation_errors
            }), 400
        
        # Create or update vehicle
        if vehicle_id:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return jsonify({
                    'success': False,
                    'message': 'Vehicle not found'
                }), 404
            action = 'updated'
            # Log the update
            current_app.logger.info(f"Updating vehicle {vehicle_id} by user {current_user.id}")
        else:
            vehicle = Vehicle()
            action = 'created'
            vehicle.created_by = current_user.id
            current_app.logger.info(f"Creating new vehicle by user {current_user.id}")
        
        # Update vehicle attributes with type conversion and null handling
        vehicle.make = data['make'].strip()
        vehicle.model = data['model'].strip()
        vehicle.year = int(data['year'])
        vehicle.registration_number = data['registration_number'].strip()
        vehicle.price_per_day = float(data['price_per_day'])
        vehicle.vehicle_type = data.get('vehicle_type', '').strip()
        
        # Handle boolean fields
        for bool_field in ['is_available', 'has_gps', 'has_bluetooth', 'has_air_conditioning']:
            if bool_field in data:
                setattr(vehicle, bool_field, str(data[bool_field]).lower() in ('true', '1', 'yes'))
        
        # Handle optional numeric fields
        for num_field in ['mileage', 'seats', 'doors']:
            if num_field in data and data[num_field]:
                try:
                    setattr(vehicle, num_field, int(float(data[num_field])))
                except (ValueError, TypeError):
                    pass  # Keep existing value if conversion fails
        
        # Handle other optional fields
        for field in ['description', 'transmission', 'fuel_type', 'color']:
            if field in data:
                setattr(vehicle, field, data[field].strip() if data[field] else None)
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                # Delete old image if exists
                if vehicle.image_url and os.path.exists(vehicle.image_url.lstrip('/')):
                    try:
                        os.remove(vehicle.image_url.lstrip('/'))
                    except OSError:
                        pass
                
                # Save new image
                file_ext = os.path.splitext(file.filename)[1].lower()
                filename = f"{vehicle.registration_number}_{secrets.token_hex(8)}{file_ext}"
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'vehicles')
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                vehicle.image_url = f"/static/uploads/vehicles/{filename}"
        
        # Set updated timestamp and user
        vehicle.updated_at = datetime.utcnow()
        vehicle.updated_by = current_user.id
        
        # Save to database
        if not vehicle_id:
            db.session.add(vehicle)
        
        db.session.commit()
        
        # Log successful operation
        current_app.logger.info(f"Vehicle {vehicle.id} {action} successfully")
        
        return jsonify({
            'success': True,
            'message': f'Vehicle {action} successfully',
            'data': {
                'id': vehicle.id,
                'make': vehicle.make,
                'model': vehicle.model,
                'registration_number': vehicle.registration_number,
                'image_url': vehicle.image_url
            }
        })
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        current_app.logger.error(f"Error saving vehicle: {error_msg}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Failed to save vehicle: {error_msg}'
        }), 500

# API: Bulk delete vehicles
@bp.route('/api/vehicles/bulk-delete', methods=['POST'])
@login_required
@admin_required
def api_bulk_delete_vehicles():
    """
    Bulk delete multiple vehicles with validation and error handling
    """
    try:
        data = request.get_json()
        
        if not data or 'vehicle_ids' not in data or not isinstance(data['vehicle_ids'], list):
            return jsonify({
                'success': False,
                'message': 'Invalid request. Expected array of vehicle IDs.'
            }), 400
        
        vehicle_ids = [int(vid) for vid in data['vehicle_ids'] if str(vid).isdigit()]
        
        if not vehicle_ids:
            return jsonify({
                'success': False,
                'message': 'No valid vehicle IDs provided'
            }), 400
        
        # Check for vehicles with active bookings
        vehicles_with_bookings = db.session.query(Vehicle.id).join(Booking).filter(
            Vehicle.id.in_(vehicle_ids),
            Booking.status.in_(['pending', 'confirmed', 'in_progress'])
        ).distinct().all()
        
        if vehicles_with_bookings:
            booked_ids = [str(v[0]) for v in vehicles_with_bookings]
            return jsonify({
                'success': False,
                'message': f'Cannot delete vehicles with active bookings',
                'details': {
                    'vehicles_with_bookings': booked_ids
                }
            }), 400
        
        # Get vehicles to delete
        vehicles = Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).all()
        
        if not vehicles:
            return jsonify({
                'success': False,
                'message': 'No vehicles found with the provided IDs'
            }), 404
        
        # Delete associated images
        for vehicle in vehicles:
            if vehicle.image_url and os.path.exists(vehicle.image_url.lstrip('/')):
                try:
                    os.remove(vehicle.image_url.lstrip('/'))
                except OSError as e:
                    current_app.logger.error(f"Error deleting image for vehicle {vehicle.id}: {str(e)}")
        
        # Delete vehicles
        delete_count = Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        current_app.logger.info(f"Bulk deleted {delete_count} vehicles by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {delete_count} vehicles',
            'count': delete_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk delete: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Failed to delete vehicles',
            'error': str(e)
        }), 500

# API: Toggle vehicle availability
@bp.route('/api/vehicles/<int:vehicle_id>/toggle-availability', methods=['POST'])
@login_required
@admin_required
def toggle_vehicle_availability(vehicle_id):
    """
    Toggle vehicle availability status
    """
    try:
        vehicle = Vehicle.query.get(vehicle_id)
        
        if not vehicle:
            return jsonify({
                'success': False,
                'message': 'Vehicle not found'
            }), 404
        
        # Toggle availability
        vehicle.is_available = not vehicle.is_available
        vehicle.updated_at = datetime.utcnow()
        vehicle.updated_by = current_user.id
        
        db.session.commit()
        
        status = 'available' if vehicle.is_available else 'unavailable'
        current_app.logger.info(f"Toggled vehicle {vehicle_id} availability to {status} by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': f'Vehicle marked as {status}',
            'data': {
                'id': vehicle.id,
                'is_available': vehicle.is_available
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling vehicle availability: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Failed to update vehicle availability'
        }), 500

# API: List all bookings
@bp.route('/api/bookings', methods=['GET'])
@login_required
@admin_required
def api_list_bookings():
    try:
        # Get query parameters
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)
        vehicle_id = request.args.get('vehicle_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Start building the query
        query = Booking.query
        
        # Apply filters
        if status:
            query = query.filter(Booking.status == status)
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        if vehicle_id:
            query = query.filter(Booking.vehicle_id == vehicle_id)
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date)
                query = query.filter(Booking.start_date >= start_date)
            except ValueError:
                pass
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date)
                query = query.filter(Booking.end_date <= end_date)
            except ValueError:
                pass
                
        # Execute query
        bookings = query.order_by(Booking.start_date.desc()).all()
        
        # Format response
        result = []
        for booking in bookings:
            try:
                result.append({
                    'id': booking.id,
                    'vehicle_id': booking.vehicle_id,
                    'user_id': booking.user_id,
                    'start_date': booking.start_date.isoformat(),
                    'end_date': booking.end_date.isoformat(),
                    'total_price': float(booking.total_price) if booking.total_price else None,
                    'status': booking.status,
                    'created_at': booking.created_at.isoformat(),
                    'vehicle': {
                        'make': booking.vehicle.make if booking.vehicle else 'Unknown',
                        'model': booking.vehicle.model if booking.vehicle else 'Unknown',
                        'image_url': booking.vehicle.image_url if booking.vehicle else ''
                    },
                    'user': {
                        'first_name': booking.user.first_name if booking.user else 'Unknown',
                        'last_name': booking.user.last_name if booking.user else 'User',
                        'email': booking.user.email if booking.user else ''
                    }
                })
            except Exception as e:
                current_app.logger.error(f'Error formatting booking {booking.id}: {str(e)}')
                continue
                
        return jsonify({
            'success': True,
            'bookings': result
        })
    except Exception as e:
        current_app.logger.error(f'Error fetching bookings: {str(e)}')
        return jsonify({'success': False, 'error': 'Failed to fetch bookings'}), 500

# API: Update booking status (HTML form submission)
@bp.route('/api/bookings/<int:booking_id>/status', methods=['POST'])
@login_required
@admin_required
def api_update_booking_status(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        new_status = request.form.get('status', '').lower()
        notes = request.form.get('notes', '')
        
        # Validate status
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed', 'active']
        if new_status not in valid_statuses:
            flash(f'Invalid status. Must be one of: {valid_statuses}', 'danger')
            return redirect(url_for('admin.bookings'))
            
        # Update status and notes
        booking.status = new_status
        booking.notes = notes if notes else booking.notes
        db.session.commit()
        
        flash(f'Booking #{booking_id} status updated to {new_status}', 'success')
        return redirect(url_for('admin.bookings'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error updating booking status: {str(e)}')
        flash('Failed to update booking status', 'danger')
        return redirect(url_for('admin.bookings'))

# API: Delete booking (HTML form submission)
@bp.route('/api/bookings/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def api_delete_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        flash('Booking deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting booking. Please try again.', 'error')
    return redirect(url_for('admin_ui.bookings'))

# Handle Chrome DevTools requests to prevent 404 errors
@bp.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    return '', 204  # Return empty 204 No Content response
