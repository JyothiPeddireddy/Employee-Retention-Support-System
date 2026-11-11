import apiClient from './client';

export const roleApi = {
  listRoles: async (params = {}) => {
    const res = await apiClient.get('/roles', { params });
    return res.data.data;
  },

  createRole: async (data) => {
    const res = await apiClient.post('/roles', data);
    return res.data.data;
  },
};
