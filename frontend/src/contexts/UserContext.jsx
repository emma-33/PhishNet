import { createContext, useContext, useState } from 'react'

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

  const isAuthenticated = () => !!user
  const isAdmin = () => user?.is_admin === true
  
  return (
    <UserContext.Provider value={{ user, setUser, isAuthenticated, isAdmin }}>
      {children}
    </UserContext.Provider>
  )
}
