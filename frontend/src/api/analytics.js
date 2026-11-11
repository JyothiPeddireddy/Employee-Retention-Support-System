import apiClient from './client';

export const analyticsApi = {
  getOverview: async () => {
    const res = await apiClient.get('/analytics/overview');
    return res.data.data; // OverviewMetrics
  },

  getTeamSummaries: async () => {
    const res = await apiClient.get('/analytics/team-summary');
    return res.data.data; // List[DepartmentMetricSummary]
  },

  getTrends: async () => {
    const res = await apiClient.get('/analytics/trends');
    return res.data.data; // List[TrendDataPoint]
  },
};
