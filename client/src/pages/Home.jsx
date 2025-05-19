import React from "react";
import "./Home.scss";
import LogoFull from "../assets/images/logo-black-full.png";
import Button from "../components/Button";

export default function Home() {
  return (
    <div className="page" id="home">
      {/* hero section */}
      <div className="section-container">
        <section id="hero">
          <div className="image-container">
            <img src={LogoFull} alt="" />
          </div>
          <div className="cta-button-group">
            <Button type="primary">Log in</Button>
            <Button type="text">CREATE AN ACCOUNT</Button>
          </div>
        </section>
      </div>
    </div>
  );
}
