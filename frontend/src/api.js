import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getItems = (userId) => api.get(`/items/${userId}`);
export const createItem = (data) => api.post('/items/', data);
export const toggleItem = (itemId) => api.patch(`/items/${itemId}`);

export default api;
