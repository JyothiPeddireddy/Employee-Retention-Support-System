import apiClient from './client';

export const interventionApi = {
  listInterventions: async (params = {}) => {
    const res = await apiClient.get('/interventions', { params });
    return res.data.data; // PaginatedResponse
  },

  createIntervention: async (data) => {
    const res = await apiClient.post('/interventions', data);
    return res.data.data;
  },

  getInterventionDetail: async (interventionId) => {
    const res = await apiClient.get(`/interventions/${interventionId}`);
    return res.data.data;
  },

  updateStatus: async (interventionId, data) => {
    const res = await apiClient.put(`/interventions/${interventionId}/status`, data);
    return res.data;
  },

  updateOutcome: async (interventionId, data) => {
    const res = await apiClient.put(`/interventions/${interventionId}/outcome`, data);
    return res.data;
  },

  recordEvent: async (interventionId, data) => {
    const res = await apiClient.post(`/interventions/${interventionId}/events`, data);
    return res.data.data;
  },
};
