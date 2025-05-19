// Routes.js
import Home from "../pages/Home";
import SignIn from "../pages/SignIn";
import HomeIcon from "@mui/icons-material/Home";
import AccountBoxIcon from "@mui/icons-material/AccountBox";

const routes = [
  {
    path: "/home",
    label: "Home",
    locationLabel: "Ranger Rental",
    element: <Home />,
    icon: <HomeIcon />,
  },
  {
    path: "/signin",
    label: "Sign In",
    locationLabel: "Sign In",
    element: <SignIn />,
    icon: <AccountBoxIcon />,
  },
];

export default routes;
