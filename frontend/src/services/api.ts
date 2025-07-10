import { store } from '../store';

const BASE_URL = 'http://localhost:8000/api';

const apiService = async (endpoint: string, options: RequestInit = {}) => {
  const { auth } = store.getState();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (auth.accessToken) {
    headers['Authorization'] = `Bearer ${auth.accessToken}`;
  }

  const response = await fetch(`${BASE_URL}/${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json();
    // DRF a menudo devuelve errores en un objeto, no solo en 'detail'
    const errorMessage = errorData.detail || JSON.stringify(errorData);
    throw new Error(errorMessage);
  }

  // Algunas respuestas (como logout) pueden no tener cuerpo
  if (response.status === 204) {
    return null;
  }

  return response.json();
};

export default apiService;