import { createBrowserRouter } from "react-router-dom"

import PublicLayout from "../layouts/PublicLayout"
import ProtectedLayout from "../layouts/ProtectedLayout"
import RequireAuth from "../auth/RequireAuth"

import LandingPage from "../pages/public/LandingPage"
import Login from "../pages/public/Login"
import Dashboard from "../pages/protected/Dashboard"

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { path: "/", element: <LandingPage /> },
      { path: "/login", element: <Login /> },
    ],
  },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <ProtectedLayout />,
        children: [
          { path: "/dashboard", element: <Dashboard /> },
        ],
      },
    ],
  },
])
