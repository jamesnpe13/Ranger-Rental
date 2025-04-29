# Ranger Rental
### Vehicle Rental App

### Overview

Vehicle Rental App is a full-stack web application designed to simplify vehicle rentals. Customers can easily browse available vehicles, plan routes, and get real-time cost estimates based on distance and vehicle type. Admins can manage the fleet, handle bookings, and track availability through a dedicated dashboard. Built with a React frontend, Flask backend, and MySQL database, the app delivers a fast, responsive, and user-friendly rental experience.

### Customer Portal

The Customer portal provides users with an intuitive interface to manage their vehicle rental experience. Customers can view available vehicles, check pricing and availability, and make bookings. The dashboard also displays upcoming reservations, past rental history, and the ability to modify or cancel bookings. Integrated with real-time data, users receive up-to-date information about vehicle availability and estimated costs based on their selected routes. Additionally, the dashboard ensures a smooth, responsive user experience across devices, with secure authentication via JWT.

### Admin Portal

The Admin Portal offers a comprehensive management interface for overseeing all aspects of the vehicle rental system. Admins can add, update, or remove vehicles from the fleet, manage pricing, and track the status of rentals in real-time. The portal provides detailed insights into current and past bookings, allowing admins to monitor customer activity, approve or cancel reservations, and manage vehicle availability. It also includes a powerful dashboard for analytics, showing rental trends and operational statistics. The portal is secured with JWT authentication and designed for optimal performance, enabling admins to make data-driven decisions efficiently.


## Features

- User authentication (Customer and Admin roles)
- Vehicle listing and booking
- Admin dashboard for managing vehicles, bookings, and accounts
- Customer dashboard
- Route Estimation & Cost Calculation
- Real-time availability updates
- Responsive design for desktop and mobile

## Tech Stack

- **Frontend:** React.js
- **Backend:** Flask (Python)
- **Database:** MySQL
- **Other Tools:** SQLAlchemy, Axios, JWT Authentication

## Getting Started

### Frontend Setup (React)

1. Navigate to the frontend directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React app:
   ```bash
   npm start
   ```


### Backend Setup (Flask)

1. Navigate to backend directory:
   ```bash
   cd server
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables (e.g., database URL, secret keys).

4. Run the Flask server:
   ```bash
   flask run
   ```

## Future Improvements

- Online payment integration
- Booking cancellations and refunds
- Push notifications (email or SMS)
- Multi-language support

### Collaborators

<span style="color:gray">*James Elazegui and Pitchaya Utaisincharoen*</span>

