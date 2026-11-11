import apiClient from './client';

export const employeeApi = {
  listEmployees: async (params = {}) => {
    const res = await apiClient.get('/employees', { params });
    return res.data.data; // PaginatedResponse: { items, total, page, page_size, total_pages }
  },

  createEmployee: async (data) => {
    const res = await apiClient.post('/employees', data);
    return res.data.data;
  },

  getEmployee: async (employeeId) => {
    const res = await apiClient.get(`/employees/${employeeId}`);
    return res.data.data;
  },

  updateEmployee: async (employeeId, data) => {
    const res = await apiClient.put(`/employees/${employeeId}`, data);
    return res.data.data;
  },

  getEmployeeTimeline: async (employeeId) => {
    const res = await apiClient.get(`/employees/${employeeId}/timeline`);
    return res.data.data; // EmployeeTimeline: { employee, tenure_history, workload_history, survey_history, promotions, attrition_outcome }
  },

  getPrioritizedList: async (params = {}) => {
    const res = await apiClient.get('/employees/prioritized', { params });
    return res.data.data; // PaginatedResponse: { items, total, page, page_size, total_pages }
  },

  getPrioritizationSummary: async () => {
    const res = await apiClient.get('/employees/summary');
    return res.data.data; // PrioritizationSummary: { total_evaluated, high_priority_count, medium_priority_count, low_priority_count, ... }
  },
};
