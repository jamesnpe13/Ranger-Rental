import React from "react";
import LogoFull from "../assets/images/logo-black-full.png";
import "./SignIn.scss";
import InputField from "../components/InputField";
import Button from "../components/Button";

export default function SignIn() {
  return (
    <div className="page" id="sign-in">
      <div className="section-container">
        <section id="form">
          <div className="image-container">
            <img src={LogoFull} alt="" />
          </div>
          <h2>Customer Sign In</h2>
          <form className="form">
            <InputField type="text" placeholder="Email" />
            <InputField type="password" placeholder="Password" />
            <Button type="primary" buttonType="submit">
              Sign In
            </Button>
          </form>
          <div className="extra-buttons">
            <Button type="text left">Forgot password</Button>
            <Button type="text left">Create account</Button>
            <Button type="text left">Sign in as administrator</Button>
          </div>
        </section>
      </div>
    </div>
  );
}
