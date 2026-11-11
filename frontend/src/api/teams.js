import apiClient from './client';

export const teamApi = {
  listTeams: async (params = {}) => {
    const res = await apiClient.get('/teams', { params });
    return res.data.data;
  },

  createTeam: async (data) => {
    const res = await apiClient.post('/teams', data);
    return res.data.data;
  },

  getTeamMembers: async (teamId) => {
    const res = await apiClient.get(`/teams/${teamId}/members`);
    return res.data.data;
  },

  transferEmployee: async (teamId, data) => {
    const res = await apiClient.post(`/teams/${teamId}/transfer`, data);
    return res.data;
  },
};
