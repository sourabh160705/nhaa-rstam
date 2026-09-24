import axios from 'axios';

// In production (Netlify), VITE_API_URL points to Render backend
// In development, Vite proxy handles /api/v1 → localhost:8000
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

const axiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  assessVoice: (formData) => axiosInstance.post('/assess/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  assessText: (data) => axiosInstance.post('/assess/text', data),
  assessCombined: (formData) => axiosInstance.post('/assess/combined', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getAssessment: (caseId) => axiosInstance.get(`/assess/${caseId}`),
  getRecommendations: (caseId) => axiosInstance.get(`/assess/${caseId}/recommendations`),
  recordConsent: (data) => axiosInstance.post('/consent/record', data),
  getCases: (params) => axiosInstance.get('/cases', { params }),
  getCaseDetail: (caseId) => axiosInstance.get(`/cases/${caseId}`),
  getDashboardStats: () => axiosInstance.get('/dashboard/stats'),
  getAlerts: () => axiosInstance.get('/dashboard/alerts'),
  getTrends: () => axiosInstance.get('/dashboard/trends')
};
