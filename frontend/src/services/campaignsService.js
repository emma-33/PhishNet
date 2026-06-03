import { apiRequest } from '../config/api'

/**
 * Get all campaigns.
 */
export const getCampaigns = async () => {
    try {
        const response = await apiRequest('/campaigns')
        return response.campaigns
    } catch (error) {
        console.error('Error getting campaigns:', error)
        throw error
    }
}

/**
 * Get a campaign by its ID.
 */
export const getCampaign = async (campaignId) => {
    try {
      const response = await apiRequest(`/campaigns/${campaignId}`)
      return response
    } catch (error) {
      console.error(`Error fetching campaign ${campaignId}:`, error)
      throw error
    }
}

/**
 * Create a new campaign.
 */
export const createCampaign = async (campaignData) => {
    try {
      const response = await apiRequest('/campaigns', {
        method: 'POST',
        body: JSON.stringify(campaignData),
      })
      return response
    } catch (error) {
      console.error('Error creating campaign:', error)
      throw error
    }
}

/**
 * Delete a campaign by its ID.
 */
export const deleteCampaign = async (campaignId) => {
    try {
      const response = await apiRequest(`/campaigns/${campaignId}`, {
        method: 'DELETE',
      })
      return response
    } catch (error) {
      console.error(`Error deleting campaign ${campaignId}:`, error)
      throw error
    }
}

/**
 * Complete a campaign by its ID.
 */
export const completeCampaign = async (campaignId) => {
    try {
      const response = await apiRequest(`/campaigns/${campaignId}/complete`, {
        method: 'POST',
      })
      return response
    } catch (error) {
      console.error(`Error completing campaign ${campaignId}:`, error)
      throw error
    }
}

/**
 * Get campaign summary by its ID.
 */
export const getCampaignSummary = async (campaignId) => {
    try {
      const response = await apiRequest(`/campaigns/${campaignId}/summary`)
      return response
    } catch (error) {
      console.error(`Error fetching campaign summary ${campaignId}:`, error)
      throw error
    }
}
