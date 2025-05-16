import React from "react";
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "500px",
};

const center = {
  lat: -36.8485,
  lng: 174.7633,
};

export default function Home() {
  return (
    <div className="page">
      <section>
        <p>Home</p>

        <LoadScript googleMapsApiKey="AIzaSyB41EEwAtfEay86VMXN5r5UJ6qILh0Lk44">
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={center}
            zoom={13}
          >
            <Marker position={center} />
          </GoogleMap>
        </LoadScript>
      </section>
    </div>
  );
}
