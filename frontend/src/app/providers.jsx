import { AuthProvider } from "../auth/AuthContext"
import { UserProvider } from "../contexts/UserContext"

export function Providers({ children }) {
  return (
    <AuthProvider>
      <UserProvider>
        {children}
      </UserProvider>
    </AuthProvider>
  )
}
