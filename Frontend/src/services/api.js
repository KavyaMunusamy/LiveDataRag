import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for handling errors
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        
        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            try {
                // Attempt to refresh token
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
                        refresh_token: refreshToken
                    });
                    
                    const { access_token } = response.data;
                    localStorage.setItem('access_token', access_token);
                    
                    // Retry original request
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed, redirect to login
                localStorage.clear();
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        
        // Handle other errors
        if (error.response?.status === 500) {
            console.error('Server error:', error.response.data);
        }
        
        return Promise.reject(error);
    }
);

// API methods
export const apiService = {
    // System
    getStatus: () => api.get('/api/v1/system/status'),
    getStats: () => api.get('/api/v1/system/stats'),
    
    // Data
    getDataStreams: () => api.get('/api/v1/data/streams'),
    getDataPoints: (params) => api.get('/api/v1/data/points', { params }),
    
    // Actions
    getActionHistory: (limit = 20) => api.get('/api/v1/actions/history', { params: { limit } }),
    confirmAction: (actionId, confirm = true) => 
        api.post(`/api/v1/actions/confirm/${actionId}`, { confirm }),
    
    // Query
    processQuery: (query, context = {}) => 
        api.post('/api/v1/query', { query, context }),
    
    // Rules
    getRules: () => api.get('/api/v1/rules'),
    createRule: (rule) => api.post('/api/v1/rules', rule),
    updateRule: (id, rule) => api.put(`/api/v1/rules/${id}`, rule),
    deleteRule: (id) => api.delete(`/api/v1/rules/${id}`),
    testRule: (rule) => api.post('/api/v1/rules/test', rule),
    
    // Monitoring
    getLogs: (params) => api.get('/api/v1/monitoring/logs', { params }),
    getMetrics: (params) => api.get('/api/v1/monitoring/metrics', { params }),
    
    // File upload for custom data sources
    uploadDataSource: (file, config) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('config', JSON.stringify(config));
        return api.post('/api/v1/data/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    }
};

export { api };