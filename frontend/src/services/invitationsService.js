import apiClient from './api'

/**
 * Create a new invitation for a tenant.
 */
export const createInvitation = async (tenantId, expiresDays = null) => {
    try {
        const response = await apiClient.post('/api/tenant-invitations', {
            tenant_id: tenantId,
            expires_days: expiresDays,
        })
        return response.data
    } catch (error) {
        console.error('Error creating invitation:', error.response?.data || error.message)
        throw error
    }
}

/**
 * Get all invitations for a tenant.
 */
export const getInvitationsByTenant = async (tenantId, isUsed = null) => {
    try {
        const params = {}
        if (isUsed !== null) {
            params.is_used = isUsed
        }

        const response = await apiClient.get(`/api/tenant-invitations/tenant/${tenantId}`, { params })
        return response.data.invitations
    } catch (error) {
        console.error('Error getting invitations:', error.response?.data || error.message)
        throw error
    }
}
