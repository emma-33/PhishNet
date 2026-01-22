import apiClient from "./api"

/**
 * Get all templates.
 */
export const getTemplates = async () => {
    try {
        const response = await apiClient.get('/api/templates')
        return response.data.templates
    } catch (error) {
        console.error('Error getting templates:', error.response?.data || error.message)
        throw error
    }
}

/**
 * Get a template by its ID.
 */
export const getTemplate = async (templateId) => {
    try {
        const response = await apiClient.get(`/api/templates/${templateId}`)
        return response.data
    } catch (error) {
        console.error(`Error fetching template ${templateId}:`, error.response?.data || error.message)
        throw error
    }
}

/**
 * Create a new template.
 */
export const createTemplate = async (templateData) => {
    try {
        const response = await apiClient.post('/api/templates', templateData)
        return response.data
    } catch (error) {
        console.error('Error creating template:', error.response?.data || error.message)
        throw error
    }
}

/**
 * Update a template by its ID.
 */
export const updateTemplate = async (templateId, templateData) => {
    try {
        const response = await apiClient.put(`/api/templates/${templateId}`, templateData)
        return response.data
    } catch (error) {
        console.error(`Error updating template ${templateId}:`, error.response?.data || error.message)
        throw error
    }
}

/**
 * Delete a template by its ID.
 */
export const deleteTemplate = async (templateId) => {
    try {
        const response = await apiClient.delete(`/api/templates/${templateId}`)
        return response.data
    } catch (error) {
        console.error(`Error deleting template ${templateId}:`, error.response?.data || error.message)
        throw error
    }
}
