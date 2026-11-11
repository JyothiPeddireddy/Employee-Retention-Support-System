import apiClient from './client';

export const compensationApi = {
  listBands: async (params = {}) => {
    const res = await apiClient.get('/compensation/bands', { params });
    return res.data.data;
  },

  createBand: async (data) => {
    const res = await apiClient.post('/compensation/bands', data);
    return res.data.data;
  },

  listPromotions: async (params = {}) => {
    const res = await apiClient.get('/compensation/promotions', { params });
    return res.data.data;
  },

  recordPromotion: async (data) => {
    const res = await apiClient.post('/compensation/promotions', data);
    return res.data.data;
  },
};
