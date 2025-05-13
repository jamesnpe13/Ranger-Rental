// Routes.js
import SignIn from "../pages/SignIn";
import Register from "../pages/Register";
import Home from "../pages/Home";
import HomeIcon from "@mui/icons-material/Home";
import AccountBoxIcon from "@mui/icons-material/AccountBox";
import CreateIcon from "@mui/icons-material/Create";

const routes = [
  {
    path: "/home",
    label: "Home",
    element: <Home />,
    icon: <HomeIcon />,
  },
  {
    path: "/signin",
    label: "Sign In",
    element: <SignIn />,
    icon: <AccountBoxIcon />,
  },
  {
    path: "/register",
    label: "Register",
    element: <Register />,
    icon: <CreateIcon />,
  },
];

export default routes;
