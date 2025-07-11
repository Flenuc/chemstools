import { store } from '@/store';

const BASE_URL = 'http://localhost:8000/api';

const apiService = async (endpoint: string, options: RequestInit = {}) => {
  const { auth } = store.getState();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  if (auth.accessToken) {
    headers['Authorization'] = `Bearer ${auth.accessToken}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  const response = await fetch(`${BASE_URL}/${endpoint}`, config);

  if (!response.ok) {
    let errorMessage = `Error del servidor (${response.status})`;
    const responseClone = response.clone(); 
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || JSON.stringify(errorData);
    } catch (e) {
      const errorText = await responseClone.text();
      console.error("La respuesta de error no es JSON. Contenido:", errorText);
      errorMessage = "Error inesperado del servidor. Revisa la consola del backend.";
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) {
      return null;
  }

  return response.json();
};

export default apiService;
