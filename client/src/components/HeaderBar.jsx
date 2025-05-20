import * as React from "react";
import "./HeaderBar.scss";
import HamburgerMenu from "./HamburgerMenu";
import logo from "../assets/images/logo-white-simple.png";
import { useNavigate, useLocation } from "react-router-dom";
import routes from "../routes/Routes";
import { useSelector } from "react-redux";

export default function HeaderBar() {
  const location = useLocation();
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);

  const match = routes.find((route) => route.path === location.pathname);
  const label = () => {
    if (match) {
      if (location.pathname == "/home" || location.pathname == "/") {
        if (auth.user.role) return `Hi, ${auth.user.firstName}!`;
      }
      return match.locationLabel;
    } else {
      return "Unknown Page";
    }
  };

  return (
    <div className="header-bar">
      <div className="logo-container" onClick={() => navigate("/")}>
        <img className="logo" src={logo} alt="" />
      </div>
      <p className="location">{label()}</p>
      <HamburgerMenu />
    </div>
  );
}
