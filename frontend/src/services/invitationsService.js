import { apiRequest } from '../config/api'

/**
 * Create a new invitation for a tenant.
 */
export const createInvitation = async (tenantId, expiresDays = null) => {
    try {
        const response = await apiRequest('/tenant-invitations', {
            method: 'POST',
            body: JSON.stringify({
                tenant_id: tenantId,
                expires_days: expiresDays
            }),
        })
        return response
    } catch (error) {
        console.error('Error creating invitation:', error)
        throw error
    }
}

/**
 * Get all invitations for a tenant.
 */
export const getInvitationsByTenant = async (tenantId, isUsed = null) => {
    try {
        const params = new URLSearchParams()
        if (isUsed !== null) {
            params.append('is_used', isUsed.toString())
        }
        const queryString = params.toString()
        const url = `/tenant-invitations/tenant/${tenantId}${queryString ? `?${queryString}` : ''}`
        const response = await apiRequest(url)
        return response.invitations
    } catch (error) {
        console.error('Error getting invitations:', error)
        throw error
    }
}
