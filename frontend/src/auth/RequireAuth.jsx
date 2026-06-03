import { Navigate, Outlet } from "react-router-dom"
import { useUser } from "../contexts/UserContext"

export default function RequireAuth() {
  const { isAuthenticated, loading } = useUser()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-white">Loading...</div>
      </div>
    )
  }

  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
