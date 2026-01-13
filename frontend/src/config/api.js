const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api"

export const getAuthToken = () => {
    return localStorage.getItem('auth_token')
}

export const setAuthToken = (token) => {
    localStorage.setItem('auth_token', token)
}

export const removeAuthToken = () => {
    localStorage.removeItem('auth_token')
}

export const apiRequest = async (endpoint, options = {}) => {
    const token = getAuthToken()

    const defaultHeaders = {
        'Content-Type': 'application/json',
    }

    if (token)
        defaultHeaders['Authorization'] = `Bearer ${token}`

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config)

        if (response.status == 401) {
            removeAuthToken()
            if (window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
            throw new Error('Unauthorized. Please login again.')
        }

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.message || 'An error occurred')
        }

        return await response.json()
    } catch (error) {
        throw new Error(`${error.message || 'An error occurred'}`)
    }
}

export default {
    API_URL,
    getAuthToken,
    setAuthToken,
    removeAuthToken,
    apiRequest,
}
