import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  user: {
    firstName: "James",
    lastName: "Elazegui",
    role: null,
    isLoggedIn: true,
  },
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setUser(state, action) {
      state.user = action.payload;
    },
    clearUser(state, action) {
      state.user = null;
    },
  },
});

export const { setUser, clearUser } = authSlice.actions;
export default authSlice.reducer;
