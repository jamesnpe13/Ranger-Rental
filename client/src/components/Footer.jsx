import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Footer.scss';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <div className="footer-logo" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
              <span>Ranger</span>Rental
            </div>
            <p className="footer-about">
              Your trusted partner for premium vehicle rentals. Experience the journey with our well-maintained fleet and exceptional service.
            </p>
            <div className="social-links">
              <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
                <i className="fab fa-facebook-f"></i>
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                <i className="fab fa-twitter"></i>
              </a>
              <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
                <i className="fab fa-instagram"></i>
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                <i className="fab fa-linkedin-in"></i>
              </a>
            </div>
          </div>

          <div className="footer-section">
            <h3 className="footer-heading">Quick Links</h3>
            <ul className="footer-links">
              <li><Link to="/" onClick={() => window.scrollTo(0, 0)}>Home</Link></li>
              <li><Link to="/vehicles" onClick={() => window.scrollTo(0, 0)}>Vehicles</Link></li>
              <li><Link to="/about" onClick={() => window.scrollTo(0, 0)}>About Us</Link></li>
              <li><Link to="/contact" onClick={() => window.scrollTo(0, 0)}>Contact</Link></li>
              <li><Link to="/faq" onClick={() => window.scrollTo(0, 0)}>FAQ</Link></li>
              <li><Link to="/terms" onClick={() => window.scrollTo(0, 0)}>Terms & Conditions</Link></li>
              <li><Link to="/privacy" onClick={() => window.scrollTo(0, 0)}>Privacy Policy</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h3 className="footer-heading">Contact Us</h3>
            <ul className="contact-info">
              <li>
                <i className="fas fa-map-marker-alt"></i>
                <span>123 Ranger Street, City, Country</span>
              </li>
              <li>
                <i className="fas fa-phone"></i>
                <span>+1 (555) 123-4567</span>
              </li>
              <li>
                <i className="fas fa-envelope"></i>
                <span>info@rangercarrental.com</span>
              </li>
              <li>
                <i className="fas fa-clock"></i>
                <span>Mon - Fri: 9:00 AM - 7:00 PM</span>
              </li>
            </ul>
          </div>

          <div className="footer-section">
            <h3 className="footer-heading">Newsletter</h3>
            <p className="newsletter-text">Subscribe to our newsletter for the latest updates and offers.</p>
            <form className="newsletter-form">
              <div className="form-group">
                <input 
                  type="email" 
                  placeholder="Your email address" 
                  className="newsletter-input"
                  required 
                />
                <button type="submit" className="newsletter-button">
                  <i className="fas fa-paper-plane"></i>
                </button>
              </div>
            </form>
            <div className="payment-methods">
              <i className="fab fa-cc-visa" title="Visa"></i>
              <i className="fab fa-cc-mastercard" title="Mastercard"></i>
              <i className="fab fa-cc-amex" title="American Express"></i>
              <i className="fab fa-cc-paypal" title="PayPal"></i>
              <i className="fab fa-google-pay" title="Google Pay"></i>
              <i className="fab fa-apple-pay" title="Apple Pay"></i>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="copyright">
            &copy; {currentYear} RangerRental. All rights reserved.
          </div>
          <div className="footer-legal">
            <Link to="/terms">Terms of Service</Link>
            <span className="divider">|</span>
            <Link to="/privacy">Privacy Policy</Link>
            <span className="divider">|</span>
            <Link to="/cookies">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
