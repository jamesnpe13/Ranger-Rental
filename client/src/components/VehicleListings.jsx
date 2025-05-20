import React from "react";
import "./VehicleListings.scss";

export default function VehicleListings() {
  const vehicleList = [
    {
      make: "Toyota",
      model: "Vitz",
      year: "2018",
      milleage: 123000,
    },
    {
      make: "Honda",
      model: "Accord",
      year: "2014",
      milleage: 200189,
    },
    {
      make: "Mazda",
      model: "Verisa",
      year: "2004",
      milleage: 106999,
    },
  ];
  const vehicleMap = () => {
    return (
      <div className="vehicle-list-container">
        {vehicleList.map((item, index) => (
          <VehicleListItem key={index} details={item} />
        ))}
      </div>
    );
  };

  return vehicleList?.length !== 0 ? (
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
