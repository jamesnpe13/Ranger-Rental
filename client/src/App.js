import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";
import HeaderBar from "./components/HeaderBar";
import FooterBar from "./components/FooterBar";
import { React } from "react";

export default function App() {
  return (
    <BrowserRouter>
      <div className="grid-container">
        <HeaderBar />
        <main>
          <div className="page-container">
            {/* This is where pages go */}
            <AppRoutes />
          </div>
          <FooterBar />
        </main>
      </div>
    </BrowserRouter>
  );
}
