import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';

const DashboardPage = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Welcome, {user?.firstName || 'User'}!</h1>
        <p>You're now logged in to your Ranger Rental account.</p>
      </div>
      
      <div className="dashboard-content">
        <div className="dashboard-card">
          <h2>Your Account</h2>
          <div className="user-info">
            <p><strong>Name:</strong> {user?.firstName} {user?.lastName}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Role:</strong> {user?.role || 'Customer'}</p>
          </div>
          <div className="dashboard-actions">
            <button 
              onClick={() => navigate('/profile')}
              className="btn btn-primary"
            >
              Edit Profile
            </button>
            <button 
              onClick={handleLogout}
              className="btn btn-secondary"
            >
              Logout
            </button>
          </div>
        </div>
        
        <div className="dashboard-card">
          <h2>Quick Actions</h2>
          <div className="quick-actions">
            <button className="action-btn">
              <span className="icon">🚗</span>
              <span>Rent a Vehicle</span>
            </button>
            <button className="action-btn">
              <span className="icon">📅</span>
              <span>View Bookings</span>
            </button>
            <button className="action-btn">
              <span className="icon">💳</span>
              <span>Payment Methods</span>
            </button>
            <button className="action-btn">
              <span className="icon">❓</span>
              <span>Help Center</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
