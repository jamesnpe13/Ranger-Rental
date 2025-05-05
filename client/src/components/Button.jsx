import React from "react";
import "./Button.scss";

export default function Button({ type }) {
  return <div className={`button ${type}`}>Button</div>;
}
