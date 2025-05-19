// set hasButton="true" to render button

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
      {props.hasButton && (
        <Button type={props.buttonType ?? "tertiary"}>
          {props.buttonLabel}
        </Button>
      )}
    </div>
  );
}
