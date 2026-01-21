import apiClient from './api';

/**
 * Audit Log API Service
 */
export const auditLogAPI = {
  /**
   * Get audit logs with pagination and filtering
   * @param {Object} params - Query parameters (page, per_page, user_id, action, resource_type)
   */
  getLogs: async (params = {}) => {
    const response = await apiClient.get('/api/audit-logs', { params });
    return response.data;
  },
};

export default auditLogAPI;
