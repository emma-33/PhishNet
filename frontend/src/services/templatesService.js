import { apiRequest } from '../config/api'

/**
 * Get all templates.
 */
export const getTemplates = async () => {
    try {
        const response = await apiRequest('/templates')
        return response.templates
    } catch (error) {
        console.error('Error getting templates:', error)
        throw error
    }
}

/**
 * Get a template by its ID.
 */
export const getTemplate = async (templateId) => {
    try {
        const response = await apiRequest(`/templates/${templateId}`)
        return response
    } catch (error) {
        console.error(`Error fetching template ${templateId}:`, error)
        throw error
    }
}

/**
 * Create a new template.
 */
export const createTemplate = async (templateData) => {
    try {
        const response = await apiRequest('/templates', {
            method: 'POST',
            body: JSON.stringify(templateData),
        })
        return response
    } catch (error) {
        console.error('Error creating template:', error)
        throw error
    }
}

/**
 * Update a template by its ID.
 */
export const updateTemplate = async (templateId, templateData) => {
    try {
        const response = await apiRequest(`/templates/${templateId}`, {
            method: 'PUT',
            body: JSON.stringify(templateData),
        })
        return response
    } catch (error) {
        console.error(`Error updating template ${templateId}:`, error)
        throw error
    }
}

/**
 * Delete a template by its ID.
 */
export const deleteTemplate = async (templateId) => {
    try {
        const response = await apiRequest(`/templates/${templateId}`, {
            method: 'DELETE',
        })
        return response
    } catch (error) {
        console.error(`Error deleting template ${templateId}:`, error)
        throw error
    }
}
