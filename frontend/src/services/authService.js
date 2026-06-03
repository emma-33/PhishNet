import apiClient, { setCsrfToken } from './api'


export const login = async (credentials, setUser) => {
    try {
        // Sends credentials to back
        const res = await apiClient.post("/api/auth/login", credentials, {
            withCredentials: true,
        })

        const { user, csrf_token } = res.data

        setUser(user)
        
        // Store CSRF token in memory
        setCsrfToken(csrf_token)

        return user
    } catch (error) {
        console.error('Error logging in:', error)
        throw error
    }
}

export const register = async (credentials, setUser) => {
    try {
        // Sends credentials to back
        const res = await apiClient.post("/api/auth/register", credentials, {
            withCredentials: true,
        })

        const {user, csrf_token} = res.data

        // Only set user if function exists
        if (user && typeof setUser === 'function') {
        setUser(user)
        }

        // Store CSRF token if present
        if (csrf_token) {
        setCsrfToken(csrf_token)
        }

        return user
    } catch (error) {
        console.error('Error registering:', error.response?.data || error.message)
        throw error
    }
}

export const logout = async (setUser) => {
    try {
        // Sends request to back
        await apiClient.post('/api/auth/logout')

        // Clears front state
        setUser(null)
    } catch (error){
        console.error('Error logging out:', error)
        throw error
    }
}
