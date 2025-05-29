import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  vehicles: [
    // {
    //   make: "Toyota",
    //   model: "Vitz",
    //   year: "2018",
    //   milleage: 123000,
    // },
    // {
    //   make: "Honda",
    //   model: "Accord",
    //   year: "2014",
    //   milleage: 200189,
    // },
    // {
    //   make: "Mazda",
    //   model: "Verisa",
    //   year: "2004",
    //   milleage: 106999,
    // },
  ],
};

const vehiclesSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {},
});

export const {} = vehiclesSlice.actions;
export default vehiclesSlice.reducer;
