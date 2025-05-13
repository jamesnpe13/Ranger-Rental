import React from "react";
import "./BookingStepper.scss";
import Button from "./Button";

import Stepper from "@mui/material/Stepper";
import Step from "@mui/material/Step";
import StepLabel from "@mui/material/StepLabel";

const steps = ["Select Vehicle", "Rental Details", "Payment", "Completed"];

export default function BookingStepper() {
  return (
    <section className="booking-stepper">
      <div className="stepper-group">
        <Stepper activeStep={2} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </div>
      <div className="button-group">
        <Button type="tertiary">Previous</Button>
        <Button type="primary">Next</Button>
      </div>
    </section>
  );
}
