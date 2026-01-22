import apiClient from "./api"

/**
 * Get all team members.
 */
export const getTeamMembers = async () => {
    try {
        const response = await apiClient.get('/api/team')
        return response.data.team_members
    } catch (error) {
        console.error('Error getting team members:', error.response?.data || error.message)
        throw error
    }
}
