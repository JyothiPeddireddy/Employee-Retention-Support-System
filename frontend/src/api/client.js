import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request Interceptor: Attach JWT Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle Token Expiration & Standard Error Messages
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // 401 Unauthorized: token expired or invalid
      if (error.response.status === 401) {
        const isAuthRoute = window.location.pathname.startsWith('/login') || window.location.pathname.startsWith('/register');
        if (!isAuthRoute) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_info');
          window.location.href = '/login?expired=1';
        }
      }
      
      const errorDetail =
        error.response.data?.detail ||
        error.response.data?.message ||
        (typeof error.response.data === 'string' ? error.response.data : 'An unexpected error occurred.');
      return Promise.reject(new Error(errorDetail));
    } else if (error.request) {
      return Promise.reject(
        new Error('Unable to connect to the backend server. Please verify FastAPI is running at ' + baseURL)
      );
    }
    return Promise.reject(error);
  }
);

export default apiClient;
