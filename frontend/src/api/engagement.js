import apiClient from './client';

export const engagementApi = {
  listSurveys: async (params = {}) => {
    const res = await apiClient.get('/engagement/surveys', { params });
    return res.data.data;
  },

  recordSurvey: async (data) => {
    const res = await apiClient.post('/engagement/surveys', data);
    return res.data.data;
  },

  updateSurvey: async (surveyId, data) => {
    const res = await apiClient.put(`/engagement/surveys/${surveyId}`, data);
    return res.data.data;
  },
};
