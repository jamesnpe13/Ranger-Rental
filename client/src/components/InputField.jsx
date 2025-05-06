import React from "react";
import Button from "./Button";
import "./InputField.scss";

export default function InputField(props) {
  return (
    <div className="input-group">
      <input
        type={props.type ?? "text"}
        id={props.id ?? ""}
        name={props.name ?? ""}
        className="input-field"
        placeholder={props.placeholder ?? "Placeholder"}
      />
      <Button type={props.buttonType ?? "tertiary"}>{props.buttonLabel}</Button>
    </div>
  );
}
