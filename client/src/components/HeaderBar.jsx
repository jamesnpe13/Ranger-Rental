import * as React from "react";
import "./HeaderBar.scss";
import HamburgerMenu from "./HamburgerMenu";
import logo from "../assets/images/logo-white-simple.png";
import { useNavigate, useLocation } from "react-router-dom";

export default function HeaderBar() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className="header-bar">
      <div className="logo-container" onClick={() => navigate("/")}>
        <img className="logo" src={logo} alt="" />
      </div>
      <p className="location">Temp loc: "{location.pathname}"</p>
      <HamburgerMenu />
    </div>
  );
}
