import apiClient from "./api"

/**
 * Get all campaigns.
 */
export const getCampaigns = async () => {
  try {
    const response = await apiClient.get('/api/campaigns')
    return response.data.campaigns
  } catch (error) {
    console.error('Error getting campaigns:', error.response?.data || error.message)
    throw error
  }
}

/**
 * Get a campaign by its ID.
 */
export const getCampaign = async (campaignId) => {
  try {
    const response = await apiClient.get(`/api/campaigns/${campaignId}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching campaign ${campaignId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Create a new campaign.
 */
export const createCampaign = async (campaignData) => {
  try {
    const response = await apiClient.post('/api/campaigns', campaignData)
    return response.data
  } catch (error) {
    console.error('Error creating campaign:', error.response?.data || error.message)
    throw error
  }
}

/**
 * Delete a campaign by its ID.
 */
export const deleteCampaign = async (campaignId) => {
  try {
    const response = await apiClient.delete(`/api/campaigns/${campaignId}`)
    return response.data
  } catch (error) {
    console.error(`Error deleting campaign ${campaignId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Complete a campaign by its ID.
 */
export const completeCampaign = async (campaignId) => {
  try {
    const response = await apiClient.post(`/api/campaigns/${campaignId}/complete`)
    return response.data
  } catch (error) {
    console.error(`Error completing campaign ${campaignId}:`, error.response?.data || error.message)
    throw error
  }
}

/**
 * Get campaign summary by its ID.
 */
export const getCampaignSummary = async (campaignId) => {
  try {
    const response = await apiClient.get(`/api/campaigns/${campaignId}/summary`)
    return response.data
  } catch (error) {
    console.error(`Error fetching campaign summary ${campaignId}:`, error.response?.data || error.message)
    throw error
  }
}
