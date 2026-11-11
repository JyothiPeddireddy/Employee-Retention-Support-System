import apiClient from './client';

export const authApi = {
  login: async (username, password) => {
    const res = await apiClient.post('/auth/login', { username, password });
    return res.data; // TokenResponse
  },

  register: async (userData) => {
    const res = await apiClient.post('/auth/register', userData);
    return res.data.data;
  },

  getMe: async () => {
    const res = await apiClient.get('/auth/me');
    return res.data.data;
  },

  changePassword: async (currentPassword, newPassword) => {
    const res = await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return res.data;
  },

  logout: async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Continue even if server-side revocation fails
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
    }
  },
};
