import apiClient from './client';

export const assessmentApi = {
  generateAssessments: async (data = {}) => {
    const res = await apiClient.post('/assessments/generate', data);
    return res.data.data;
  },

  listRuns: async (params = {}) => {
    const res = await apiClient.get('/assessments/runs', { params });
    return res.data.data;
  },

  listAssessments: async (params = {}) => {
    const res = await apiClient.get('/assessments', { params });
    return res.data.data;
  },

  getAssessmentDetail: async (assessmentId) => {
    const res = await apiClient.get(`/assessments/${assessmentId}`);
    return res.data.data;
  },
};
