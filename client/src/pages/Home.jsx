import React from "react";
import { useNavigate } from "react-router-dom";
import "./Home.scss";
import LogoFull from "../assets/images/logo-black-full.png";
import Button from "../components/Button";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="page" id="home">
      {/* hero section */}
      <div className="section-container">
        <section id="hero">
          <div className="image-container">
            <img src={LogoFull} alt="" />
          </div>
          <div className="cta-button-group">
            <Button
              type="primary"
              onClick={() => {
                navigate("/signin");
              }}
            >
              Sign In
            </Button>
            <Button type="text">Create an account</Button>
          </div>
        </section>
      </div>
    </div>
  );
}
