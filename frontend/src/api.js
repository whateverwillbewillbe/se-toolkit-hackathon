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
export const deleteItem = (itemId) => api.delete(`/items/${itemId}`);
export const clearItems = (userId) => api.delete(`/items/user/${userId}`);
export const generateRecipe = (userId) => api.post(`/generate-recipe/${userId}`);

export default api;
