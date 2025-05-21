import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import NotFound from "../pages/NotFound";
import routes from "./Routes";

export default function AppRoutes() {
  return (
    <Routes>
      {routes.map(({ path, element }) => (
        <Route key={path} path={path} element={element} />
      ))}

      <Route path={"/"} element={<Navigate to="/home" replace />} />
      <Route path={"*"} element={<NotFound />} />
    </Routes>
  );
}
