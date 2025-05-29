import React from "react";
import "./Button.scss";

export default function Button(props) {
  return (
    <button
      type={props.buttonType}
      onClick={props.onClick}
      className={`button ${props.type}`}
    >
      <span>{props.children}</span>
    </button>
  );
}
