import React from "react";
import "./Chip.scss";

export default function Chip(props) {
  return (
    <div className="chip">
      <span className="sub">{props.label ?? "Chip"}</span>
    </div>
  );
}
