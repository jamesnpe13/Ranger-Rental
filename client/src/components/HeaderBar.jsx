import React from "react";
import "./HeaderBar.scss";
import simpleWhiteLogo from "../assets/images/logo-white-simple.png";

export default function HeaderBar() {
  return (
    <div className="header-bar">
      <div className="logo-container">
        <img
          className="logo"
          src={simpleWhiteLogo}
          alt="logo"
        />
      </div>

      <p className="location">Location</p>

      <div className="hamburger">
        <div className="bar" />
        <div className="bar" />
        <div className="bar" />
      </div>
    </div>
  );
}
