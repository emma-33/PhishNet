import { createContext, useContext, useState, useEffect } from 'react'
import { getAuthToken } from '../config/api'

const UserContext = createContext(null)

export const useUser = () => {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (error) {
        console.error('Error parsing user data:', error)
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const setUserData = (userData) => {
    setUser(userData)
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }

  const isAdmin = () => {
    return user?.is_admin === true
  }

  const isAuthenticated = () => {
    return !!getAuthToken() && !!user
  }

  return (
    <UserContext.Provider value={{ user, setUser: setUserData, isAdmin, isAuthenticated, loading }}>
      {children}
    </UserContext.Provider>
  )
}
