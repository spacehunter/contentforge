import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    let token = localStorage.getItem('token');
    // Fallback: try sessionStorage or any stored auth token
    if (!token) {
      token = sessionStorage.getItem('token');
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const auth = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

export const brands = {
  create: (data) => api.post('/brands', data),
  list: () => api.get('/brands'),
};

export const content = {
  generate: (data) => api.post('/content/generate', data),
  generateImage: (data) => api.post('/content/generate-image', data),
  list: () => api.get('/content'),
};

export const billing = {
  checkout: (plan_id: string) => api.post('/billing/checkout', { plan_id }),
  subscription: () => api.get('/billing/subscription'),
  portal: () => api.post('/billing/portal'),
};

export const subscriptions = {
  plans: () => api.get('/subscriptions/plans'),
};

export const billing = {
  checkout: (plan_id: string) => api.post('/billing/checkout', { plan_id }),
  subscription: () => api.get('/billing/subscription'),
  portal: () => api.post('/billing/portal'),
};

export default api;
