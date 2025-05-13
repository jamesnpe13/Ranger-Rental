import { BrowserRouter } from "react-router-dom";
import BookingStepper from "./components/BookingStepper";
import Button from "./components/Button";
import Chip from "./components/Chip";
import FooterBar from "./components/FooterBar";
import HeaderBar from "./components/HeaderBar";
import InputField from "./components/InputField";
import AppRoutes from "./routes/AppRoutes";

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
