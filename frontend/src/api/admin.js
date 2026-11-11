import apiClient from './client';

export const adminApi = {
  listUsers: async (params = {}) => {
    const res = await apiClient.get('/admin/users', { params });
    return res.data.data;
  },

  createUser: async (data) => {
    const res = await apiClient.post('/admin/users', data);
    return res.data.data;
  },

  updateUserRole: async (userId, role) => {
    const res = await apiClient.put(`/admin/users/${userId}/role`, { role });
    return res.data.data;
  },

  getSystemStats: async () => {
    const res = await apiClient.get('/admin/system-stats');
    return res.data.data; // SystemStatsResponse
  },

  getAuditLogs: async (params = {}) => {
    const res = await apiClient.get('/admin/audit-logs', { params });
    return res.data.data;
  },
};
