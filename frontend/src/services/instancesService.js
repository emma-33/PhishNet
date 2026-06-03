import apiClient from "./api"

/**
 * Get all instances.
 */
export const getInstances = async () => {
  try {
    const response = await apiClient.get('/api/instances')
    return response.data.instances
  } catch (error) {
    console.error('Error getting instances:', error.response?.data || error.message)
    throw error
  }
}

/**
 * Get an instance by its ID.
 */
export const getInstance = async (instanceId) => {
  try {
    const response = await apiClient.get(`/api/instances/${instanceId}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching instance ${instanceId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Create a new instance.
 */
export const createInstance = async (instanceData) => {
  try {
    const response = await apiClient.post('/api/instances', instanceData)
    return response.data
  } catch (error) {
    console.error('Error creating instance:', error.response?.data || error.message)
    throw error
  }
}

/**
 * Update an instance by its ID.
 */
export const updateInstance = async (instanceId, instanceData) => {
  try {
    const response = await apiClient.put(`/api/instances/${instanceId}`, instanceData)
    return response.data
  } catch (error) {
    console.error(`Error updating instance ${instanceId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Delete an instance by its ID.
 */
export const deleteInstance = async (instanceId) => {
  try {
    const response = await apiClient.delete(`/api/instances/${instanceId}`)
    return response.data
  } catch (error) {
    console.error(`Error deleting instance ${instanceId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Toggle instance active status.
 */
export const toggleInstanceStatus = async (instanceId) => {
  try {
    const response = await apiClient.patch(`/api/instances/${instanceId}/toggle`)
    return response.data
  } catch (error) {
    console.error(`Error toggling instance ${instanceId} status:`, error.response?.data || error.message)
    throw error
  }
}
