import apiClient from './client';

export const dataQualityApi = {
  triggerValidation: async (data = { seed: 20261022, scale: 500 }) => {
    const res = await apiClient.post('/data-quality/validate', data);
    return res.data.data; // ValidationRunResponse
  },

  listValidationRuns: async (params = {}) => {
    const res = await apiClient.get('/data-quality/runs', { params });
    return res.data.data;
  },

  getRunIssues: async (runId) => {
    const res = await apiClient.get(`/data-quality/runs/${runId}/issues`);
    return res.data.data;
  },

  getGroundTruthAnomalies: async () => {
    const res = await apiClient.get('/data-quality/ground-truth');
    return res.data.data;
  },
};
