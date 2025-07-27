import { store } from '@/store';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const baseFetch = async (endpoint: string, options: RequestInit = {}) => {
  const { auth } = store.getState();
  
  // FIX: Use the Headers constructor to correctly handle different HeadersInit types.
  const headers = new Headers(options.headers);

  // Set default Content-Type for methods that typically have a body.
  // For GET/DELETE etc., it's often better not to set it unless needed.
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  // Add auth token if available
  if (auth.accessToken) {
    headers.set('Authorization', `Bearer ${auth.accessToken}`);
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  // Prevenir dobles barras en la URL
  const url = `${BASE_URL}/${endpoint.startsWith('/') ? endpoint.substring(1) : endpoint}`;
  const response = await fetch(url, config);

  if (!response.ok) {
    let errorMessage = `Error del servidor (${response.status})`;
    const responseClone = response.clone();
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.error || JSON.stringify(errorData);
    } catch (e) {
      const errorText = await responseClone.text();
      console.error("La respuesta de error no es JSON. Contenido:", errorText);
      errorMessage = "Error inesperado del servidor. Revisa la consola del backend.";
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) { // Manejar respuestas sin contenido
    return null;
  }

  return response.json();
};

// Crear un objeto con métodos para cada verbo HTTP
export const api = {
  get: (endpoint: string, options?: RequestInit) => {
    return baseFetch(endpoint, { ...options, method: 'GET' });
  },
  post: (endpoint: string, body: any, options?: RequestInit) => {
    return baseFetch(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(body),
    });
  },
  put: (endpoint: string, body: any, options?: RequestInit) => {
    return baseFetch(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(body),
    });
  },
  delete: (endpoint: string, options?: RequestInit) => {
    return baseFetch(endpoint, { ...options, method: 'DELETE' });
  },
};