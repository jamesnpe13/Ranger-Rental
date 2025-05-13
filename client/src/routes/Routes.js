// Routes.js
import SignIn from "../pages/SignIn";
import Register from "../pages/Register";
import NotFound from "../pages/NotFound";
import Home from "../pages/Home";

const routes = [
  { path: "/home", label: "Home", element: <Home /> },
  { path: "/signin", label: "Sign In", element: <SignIn /> },
  { path: "/register", label: "Register", element: <Register /> },
];

export default routes;
