import axios from 'axios';

// Dynamically sets host based on client-side location to support local networking
const getBackendBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return `http://${window.location.hostname}:8000/api`;
  }
  return 'http://backend:8000/api';
};

export const api = axios.create({
  baseURL: getBackendBaseUrl(),
});

// Interceptor to always get the correct dynamic URL
api.interceptors.request.use((config) => {
  config.baseURL = getBackendBaseUrl();
  return config;
});

export const getAiServiceUrl = () => {
  if (typeof window !== 'undefined') {
    return `http://${window.location.hostname}:8001`;
  }
  return 'http://ai-service:8001';
};
