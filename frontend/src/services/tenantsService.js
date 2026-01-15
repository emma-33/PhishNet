import { apiRequest } from '../config/api'

/**
 * Get all tenants.
 */
export const getTenants = async () => {
    try {
        const response = await apiRequest('/tenants')
        return response.tenants
    } catch (error) {
        console.error('Error getting tenants:', error)
        throw error
    }
}

/**
 * Get a tenant by its ID.
 */
export const getTenant = async (tenantId) => {
    try {
        const response = await apiRequest(`/tenants/${tenantId}`)
        return response
    } catch (error) {
        console.error(`Error fetching tenant ${tenantId}:`, error)
        throw error
    }
}

/**
 * Create a new tenant.
 */
export const createTenant = async (tenantData) => {
    try {
        const response = await apiRequest('/tenants', {
            method: 'POST',
            body: JSON.stringify(tenantData),
        })
        return response
    } catch (error) {
        console.error('Error creating tenant:', error)
        throw error
    }
}

/**
 * Update a tenant by its ID.
 */
export const updateTenant = async (tenantId, tenantData) => {
    try {
        const response = await apiRequest(`/tenants/${tenantId}`, {
            method: 'PUT',
            body: JSON.stringify(tenantData),
        })
        return response
    } catch (error) {
        console.error(`Error updating tenant ${tenantId}:`, error)
        throw error
    }
}

/**
 * Delete a tenant by its ID.
 */
export const deleteTenant = async (tenantId) => {
    try {
        const response = await apiRequest(`/tenants/${tenantId}`, {
            method: 'DELETE',
        })
        return response
    } catch (error) {
        console.error(`Error deleting tenant ${tenantId}:`, error)
        throw error
    }
}
