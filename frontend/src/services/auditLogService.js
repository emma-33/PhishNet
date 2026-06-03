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

  /**
   * Export audit logs as CSV
   * @param {Object} params - Query parameters (user_id, action, resource_type)
   */
  exportLogs: async (params = {}) => {
    const response = await apiClient.get('/api/audit-logs/export', {
      params,
      responseType: 'blob'
    });

    // Create a link to download the file
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `audit_logs_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    return response.data;
  },
};

export default auditLogAPI;
