import * as React from "react";
import "./HeaderBar.scss";
import HamburgerMenu from "./HamburgerMenu";
import logo from "../assets/images/logo-white-simple.png";
import { useNavigate, useLocation } from "react-router-dom";
import routes from "../routes/Routes";

export default function HeaderBar() {
  const location = useLocation();
  const navigate = useNavigate();

  const match = routes.find((route) => route.path === location.pathname);
  const label = match ? match.locationLabel : "Unknown Page";

  return (
    <div className="header-bar">
      <div className="logo-container" onClick={() => navigate("/")}>
        <img className="logo" src={logo} alt="" />
      </div>
      <p className="location">{label}</p>
      <HamburgerMenu />
    </div>
  );
}
