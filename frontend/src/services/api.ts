import { setTokens, logout } from '@/store/authSlice';

// Lazy import del store para evitar dependencias circulares
let store: any;
const getStore = () => {
  if (!store) {
    store = require('@/store').store;
  }
  return store;
};

// Detectar si estamos accediendo a través de nginx (puerto 80) o directamente
// Si accedemos por el puerto 80 (nginx), usar rutas relativas
// Si accedemos por el puerto 3000 (desarrollo directo), usar localhost:8000
const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // Cliente - siempre usar rutas relativas para que Next.js maneje el proxy
    return '/api';
  }
  // Servidor (SSR) - usar la URL del backend directamente
  return process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000/api';
};

const BASE_URL = getBaseUrl();

// Función para refrescar el token
const refreshAccessToken = async (): Promise<boolean> => {
  const currentStore = getStore();
  const { auth } = currentStore.getState();
  
  if (!auth.refreshToken) {
    console.warn('No refresh token available');
    return false;
  }
  
  try {
    const response = await fetch(`${BASE_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh: auth.refreshToken,
      }),
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('Token refreshed successfully');
      currentStore.dispatch(setTokens({
        access: data.access,
        refresh: data.refresh || auth.refreshToken, // Usar el nuevo refresh token si está disponible
      }));
      return true;
    } else {
      console.error('Failed to refresh token:', response.status);
    }
  } catch (error) {
    console.error('Error refreshing token:', error);
  }
  
  // Si no se pudo refrescar, hacer logout
  console.warn('Refreshing token failed, logging out user');
  currentStore.dispatch(logout());
  return false;
};

const baseFetch = async (endpoint: string, options: RequestInit = {}) => {
  const currentStore = getStore();
  const { auth } = currentStore.getState();
  
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
  let response = await fetch(url, config);

  // Si obtenemos un 401 y tenemos refresh token, intentar refrescar
  if (response.status === 401 && auth.refreshToken && !endpoint.includes('auth/token')) {
    const refreshSuccess = await refreshAccessToken();
    
    if (refreshSuccess) {
      // Retry the original request with the new token
      const newAuth = currentStore.getState().auth;
      if (newAuth.accessToken) {
        headers.set('Authorization', `Bearer ${newAuth.accessToken}`);
        response = await fetch(url, { ...config, headers });
      }
    }
  }

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