import apiClient from "./api"

/**
 * Get all tenants.
 */
export const getTenants = async () => {
  try {
    const response = await apiClient.get('/api/tenants')
    return response.data.tenants
  } catch (error) {
    console.error('Error getting tenants:', error.response?.data || error.message)
    throw error
  }
}

/**
 * Get a tenant by its ID.
 */
export const getTenant = async (tenantId) => {
  try {
    const response = await apiClient.get(`/api/tenants/${tenantId}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching tenant ${tenantId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Create a new tenant.
 */
export const createTenant = async (tenantData) => {
  try {
    const response = await apiClient.post('/api/tenants', tenantData)
    return response.data
  } catch (error) {
    console.error('Error creating tenant:', error.response?.data || error.message)
    throw error
  }
}

/**
 * Update a tenant by its ID.
 */
export const updateTenant = async (tenantId, tenantData) => {
  try {
    const response = await apiClient.put(`/api/tenants/${tenantId}`, tenantData)
    return response.data
  } catch (error) {
    console.error(`Error updating tenant ${tenantId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Delete a tenant by its ID.
 */
export const deleteTenant = async (tenantId) => {
  try {
    const response = await apiClient.delete(`/api/tenants/${tenantId}`)
    return response.data
  } catch (error) {
    console.error(`Error deleting tenant ${tenantId}:`, error.response?.data || error.message)
    throw error
  }
}
