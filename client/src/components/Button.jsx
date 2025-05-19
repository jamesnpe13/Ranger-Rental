import React from "react";
import "./Button.scss";

export default function Button({
  props,
  type = "greyed-out",
  children = "Button",
  onClick,
}) {
  return (
    <div onClick={onClick} className={`button ${type}`}>
      <span>{children}</span>
    </div>
  );
}
