import React from "react";
import "./VehicleListings.scss";
import { useSelector, useDispatch } from "react-redux";

export default function VehicleListings() {
  const vehicles = useSelector((state) => state.vehicles);
  const dispatch = useDispatch();

  const vehicleMap = () => {
    return (
      <div className="vehicle-list-container">
        {vehicles.vehicles.map((item, index) => (
          <VehicleListItem key={index} details={item} />
        ))}
      </div>
    );
  };

  return vehicles.vehicles?.length !== 0 ? (
    vehicleMap()
  ) : (
    <p>There are no vehicles to display.</p>
  );
}

export function VehicleListItem(props) {
  return (
    <div className="vehicle-list-item">
      <h5>
        {props.details.make} {props.details.model}
      </h5>
      <p>{props.details.year}</p>
    </div>
  );
}
