import React from "react";
import "./Button.scss";

export default function Button({
  props,
  type = "greyed-out",
  children = "Button",
}) {
  return (
    <div className={`button ${type}`}>
      <span>{children}</span>
    </div>
  );
}
