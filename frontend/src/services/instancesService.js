import { apiRequest } from '../config/api'

/**
 * Get all instances.
 */
export const getInstances = async () => {
    try {
        const response = await apiRequest('/instances')
        return response.instances
    } catch (error) {
        console.error('Error getting instances:', error)
        throw error
    }
}

/**
 * Get an instance by its ID.
 */
export const getInstance = async (instanceId) => {
    try {
        const response = await apiRequest(`/instances/${instanceId}`)
        return response
    } catch (error) {
        console.error(`Error fetching instance ${instanceId}:`, error)
        throw error
    }
}

/**
 * Create a new instance.
 */
export const createInstance = async (instanceData) => {
    try {
        const response = await apiRequest('/instances', {
            method: 'POST',
            body: JSON.stringify(instanceData),
        })
        return response
    } catch (error) {
        console.error('Error creating instance:', error)
        throw error
    }
}

/**
 * Update an instance by its ID.
 */
export const updateInstance = async (instanceId, instanceData) => {
    try {
        const response = await apiRequest(`/instances/${instanceId}`, {
            method: 'PUT',
            body: JSON.stringify(instanceData),
        })
        return response
    } catch (error) {
        console.error(`Error updating instance ${instanceId}:`, error)
        throw error
    }
}

/**
 * Delete an instance by its ID.
 */
export const deleteInstance = async (instanceId) => {
    try {
        const response = await apiRequest(`/instances/${instanceId}`, {
            method: 'DELETE',
        })
        return response
    } catch (error) {
        console.error(`Error deleting instance ${instanceId}:`, error)
        throw error
    }
}

/**
 * Toggle instance active status.
 */
export const toggleInstanceStatus = async (instanceId) => {
    try {
        const response = await apiRequest(`/instances/${instanceId}/toggle`, {
            method: 'PATCH',
        })
        return response
    } catch (error) {
        console.error(`Error toggling instance ${instanceId} status:`, error)
        throw error
    }
}
