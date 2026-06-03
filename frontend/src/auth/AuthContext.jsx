import { createContext, useEffect, useState } from "react"
import { jwtDecode } from "jwt-decode"
import axios from "axios"

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      setLoading(false)
      return
    }

    try {
      const decoded = jwtDecode(token)

      if (decoded.exp * 1000 < Date.now()) {
        throw new Error("Token expired")
      }

      setUser(decoded)
      axios.defaults.headers.common.Authorization = `Bearer ${token}`
    } catch {
      localStorage.removeItem("token")
      delete axios.defaults.headers.common.Authorization
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

const login = (token) => {
  const decoded = jwtDecode(token);
  setUser(decoded);
  localStorage.setItem("token", token);
  axios.defaults.headers.common.Authorization = `Bearer ${token}`;
};


  const logout = () => {
    localStorage.removeItem("token")
    delete axios.defaults.headers.common.Authorization
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}
