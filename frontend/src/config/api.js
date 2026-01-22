const API_URL = import.meta.env.VITE_API_URL || ""

// API helper, cookies automatically included
export const apiRequest = async (endpoint, options = {}) => {
    const method = options.method?.toUpperCase() || "GET"

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {}),
    }

    // Attach CSRF token for state-changing requests
    if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
        if (!csrfToken) {
            throw new Error("CSRF token not loaded")
        }
        headers["X-CSRF-TOKEN"] = csrfToken
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        method,
        headers,
        credentials: "include",
    })

    if (response.status === 401) {
        // Session expired or not authenticated
        window.location.href = "/login"
        throw new Error("Unauthorized")
    }

    // code 204 => empty response
    if (response.status === 204) {
        return null
    }

    if (!response.ok) {
        let errorMessage = "An error occurred"
        try {
            const errorData = await response.json()
            errorMessage = errorData.message || errorData.error || errorMessage
        } catch {
            //ignore JSON parse error
        }
        throw new Error(errorMessage)
    }
    return response.json()
}

export default {
    API_URL,
    apiRequest,
}
