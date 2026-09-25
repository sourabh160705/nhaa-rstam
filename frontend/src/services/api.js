import axios from 'axios';

// The live Render backend URL for this deployment
const DEFAULT_RENDER_BACKEND = 'https://nhaa-rstam.onrender.com';

// Handle trailing slashes and normalize the backend URL
let rawUrl = import.meta.env.VITE_API_URL;

// Fix common typo: nhaa-rstam-backend -> nhaa-rstam
if (rawUrl && rawUrl.includes('nhaa-rstam-backend.onrender.com')) {
  rawUrl = rawUrl.replace('nhaa-rstam-backend.onrender.com', 'nhaa-rstam.onrender.com');
}

const API_BASE = rawUrl
  ? `${rawUrl.replace(/\/$/, '')}/api/v1`
  : (import.meta.env.PROD ? `${DEFAULT_RENDER_BACKEND}/api/v1` : '/api/v1');

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
