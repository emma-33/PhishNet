import { apiRequest, removeAuthToken, setAuthToken } from '../config/api'

export const login = async (credentials) => {
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        })

        if (data.access_token) {
            setAuthToken(data.access_token)
        }

        if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user))
        }

        return data
    } catch (error) {
        console.error('Error logging in:', error)
        throw error
    }
}

export const register = async (userData) => {
    try {
        const data = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        })

        if (data.access_token) {
            setAuthToken(data.access_token)
        }

        if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user))
        }

        return data
    } catch (error) {
        console.error('Error registering:', error)
        throw error
    }
}

export const logout = async () => {
    removeAuthToken()
    localStorage.removeItem('user')
}