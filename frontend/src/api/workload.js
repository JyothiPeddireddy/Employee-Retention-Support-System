import apiClient from './client';

export const workloadApi = {
  listSnapshots: async (params = {}) => {
    const res = await apiClient.get('/workload/snapshots', { params });
    return res.data.data;
  },

  recordSnapshot: async (data) => {
    const res = await apiClient.post('/workload/snapshots', data);
    return res.data.data;
  },
};
