from flask import redirect, url_for, flash, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required, logout_user
from models import db, User, Vehicle, Booking

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('index'))
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login', next=request.url))

class VehicleAdmin(AdminModelView):
    column_list = ('id', 'make', 'model', 'year', 'price_per_day', 'is_available')
    column_searchable_list = ('make', 'model')
    column_filters = ('is_available', 'year')
    form_columns = ('make', 'model', 'year', 'price_per_day', 'is_available', 'location', 'description', 'image_url')
    page_size = 20

class BookingAdmin(AdminModelView):
    column_list = ('id', 'user.email', 'vehicle.make', 'start_date', 'end_date', 'status', 'total_price')
    column_searchable_list = ('user.email', 'vehicle.make')
    column_filters = ('status', 'start_date', 'end_date')
    page_size = 20

class UserAdmin(AdminModelView):
    column_list = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active')
    column_searchable_list = ('email', 'first_name', 'last_name')
    column_filters = ('role', 'is_active')
    form_columns = ('email', 'first_name', 'last_name', 'role', 'is_active')
    can_create = False
    page_size = 20

class CustomAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=url_for('admin.index')))
        if current_user.role != 'admin':
            flash('You do not have permission to access the admin area.', 'error')
            return redirect(url_for('index'))
        return super().index()

def init_admin(app):
    admin = Admin(
        app,
        name='RangerRental Admin',
        template_mode='bootstrap4',
        index_view=CustomAdminIndexView(
            name='Dashboard',
            template='admin/index.html',
            url='/admin'
        )
    )
    
    # Add views with custom endpoint names to avoid conflicts
    admin.add_view(VehicleAdmin(Vehicle, db.session, name='Vehicles', endpoint='admin_vehicles'))
    admin.add_view(BookingAdmin(Booking, db.session, name='Bookings', endpoint='admin_bookings'))
    admin.add_view(UserAdmin(User, db.session, name='Users', endpoint='admin_users'))
