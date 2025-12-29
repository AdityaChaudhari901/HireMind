import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('adminToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('adminToken');
            localStorage.removeItem('adminUser');
            if (!window.location.pathname.includes('/test/')) {
                window.location.href = '/admin/login';
            }
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    adminLogin: (email, password) =>
        api.post('/auth/admin/login', { email, password }),
    adminRegister: (data) =>
        api.post('/auth/admin/register', data),
    getMe: () =>
        api.get('/auth/admin/me'),
};

// Questions API
export const questionsAPI = {
    createBase: (data) =>
        api.post('/questions/base', data),
    getBase: (params) =>
        api.get('/questions/base', { params }),
    getBaseById: (id) =>
        api.get(`/questions/base/${id}`),
    deleteBase: (id) =>
        api.delete(`/questions/base/${id}`),
    createVariant: (data) =>
        api.post('/questions/variants', data),
    getVariants: (questionId, approvedOnly = false) =>
        api.get(`/questions/variants/${questionId}`, { params: { approved_only: approvedOnly } }),
    approveVariant: (variantId, approved) =>
        api.put(`/questions/variants/${variantId}/approve`, { approved }),
    getPending: (params) =>
        api.get('/questions/pending', { params }),
    generateVariants: (data) =>
        api.post('/questions/generate-variants', data),
    getTopics: () =>
        api.get('/questions/topics'),
    getStats: () =>
        api.get('/questions/stats'),
    generateQuestionsFromTopic: (data) =>
        api.post('/questions/generate-questions', data),
};

// Test API
export const testAPI = {
    generateLink: (data) =>
        api.post('/test/generate-link', data),
    getLinks: (params) =>
        api.get('/test/links', { params }),
    deleteLink: (linkId) =>
        api.delete(`/test/links/${linkId}`),
    validateLink: (linkId) =>
        api.get(`/test/${linkId}/validate`),
    startTest: (linkId, data) =>
        api.post(`/test/${linkId}/start`, data),
    getQuestion: (sessionId) =>
        api.get(`/test/session/${sessionId}/question`),
    submitAnswer: (sessionId, selectedIndex) =>
        api.post(`/test/session/${sessionId}/answer`, { selected_index: selectedIndex }),
    logTabSwitch: (sessionId) =>
        api.post(`/test/session/${sessionId}/tab-switch`),
    getSessionStatus: (sessionId) =>
        api.get(`/test/session/${sessionId}/status`),
};

// Results API
export const resultsAPI = {
    getResults: (params) =>
        api.get('/results', { params }),
    getResultDetail: (sessionId) =>
        api.get(`/results/${sessionId}`),
    getAttempts: (sessionId) =>
        api.get(`/results/${sessionId}/attempts`),
    deleteResult: (sessionId) =>
        api.delete(`/results/${sessionId}`),
    exportCSV: () =>
        api.get('/results/export/csv', { responseType: 'blob' }),
};

export default api;
