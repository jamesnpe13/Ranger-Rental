import React, { useContext, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../App';
import './HeaderBar.scss';
import logo from '../assets/images/logo-white-simple.png';

const HeaderBar = () => {
  const { isAuthenticated, user, logout } = useContext(AuthContext);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    setIsMenuOpen(false);
    navigate('/login');
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  // Don't show header on auth pages
  if (['/login', '/register'].includes(location.pathname)) {
    return null;
  }

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo-container" onClick={() => navigate('/')}>
          <img src={logo} alt="Ranger Rental" className="logo" />
          <span className="logo-text">Ranger Rental</span>
        </div>

        <nav className={`nav-links ${isMenuOpen ? 'active' : ''}`}>
          <Link to="/" className="nav-link" onClick={() => setIsMenuOpen(false)}>
            Home
          </Link>
          <Link to="/vehicles" className="nav-link" onClick={() => setIsMenuOpen(false)}>
            Vehicles
          </Link>
          <Link to="/about" className="nav-link" onClick={() => setIsMenuOpen(false)}>
            About
          </Link>
          <Link to="/contact" className="nav-link" onClick={() => setIsMenuOpen(false)}>
            Contact
          </Link>
        </nav>

        <div className="auth-section">
          {isAuthenticated ? (
            <div className="user-menu">
              <button 
                className="user-button" 
                onClick={toggleMenu}
                aria-expanded={isMenuOpen}
                aria-label="User menu"
              >
                <div className="user-avatar">
                  {user?.firstName?.charAt(0) || 'U'}
                </div>
                <span className="user-name">
                  {user?.firstName || 'User'}
                </span>
                <span className={`dropdown-arrow ${isMenuOpen ? 'up' : 'down'}`}>
                  ▼
                </span>
              </button>
              
              {isMenuOpen && (
                <div className="dropdown-menu">
                  <Link 
                    to="/dashboard" 
                    className="dropdown-item"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link 
                    to="/profile" 
                    className="dropdown-item"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    My Profile
                  </Link>
                  <div className="dropdown-divider"></div>
                  <button 
                    className="dropdown-item"
                    onClick={handleLogout}
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <Link 
                to="/login" 
                className="btn btn-outline"
                state={{ from: location.pathname }}
              >
                Login
              </Link>
              <Link 
                to="/register" 
                className="btn btn-primary"
                state={{ from: location.pathname }}
              >
                Sign Up
              </Link>
            </div>
          )}
          
          <button 
            className={`hamburger ${isMenuOpen ? 'active' : ''}`} 
            onClick={toggleMenu}
            aria-label="Toggle menu"
            aria-expanded={isMenuOpen}
          >
            <span className="hamburger-line"></span>
            <span className="hamburger-line"></span>
            <span className="hamburger-line"></span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default HeaderBar;
