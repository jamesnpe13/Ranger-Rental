import React from "react";
import { useNavigate } from "react-router-dom";
import "./Home.scss";
import LogoFull from "../assets/images/logo-black-full.png";
import Button from "../components/Button";
import { useSelector, useDispatch } from "react-redux";
import GuestHome from "./GuestHome";
import CustomerHome from "./CustomerHome";
import AdminHome from "./AdminHome";

export default function Home() {
  const navigate = useNavigate();
  const auth = useSelector((state) => state.auth);
  const dispatch = useDispatch();

  switch (auth.user.role) {
    case "customer":
      return <CustomerHome />;
    case "admin":
      return <AdminHome />;
    default:
      return <GuestHome />;
  }
}
