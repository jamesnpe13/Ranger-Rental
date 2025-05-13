import * as React from "react";
import "./HeaderBar.scss";
import HamburgerMenu from "./HamburgerMenu";
import logo from "../assets/images/logo-white-simple.png";

export default function HeaderBar() {
  return (
    <div className="header-bar">
      <div className="logo-container">
        <img
          className="logo"
          src={logo}
          alt=""
        />
      </div>
      <p className="location">Ranger Rental</p>
      <HamburgerMenu />
    </div>
  );
}
