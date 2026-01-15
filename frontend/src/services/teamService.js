import { apiRequest } from '../config/api'

/**
 * Get all team members.
 */
export const getTeamMembers = async () => {
    try {
        const response = await apiRequest('/team')
        return response.team_members
    } catch (error) {
        console.error('Error getting team members:', error)
        throw error
    }
}
