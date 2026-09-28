// Configuración de rutas públicas de la app.
// - NEXT_PUBLIC_BASE_PATH: prefijo cuando la web se sirve en un subdirectorio (p. ej. /chemstools en GitHub Pages).
// - NEXT_PUBLIC_API_URL: URL completa del backend (p. ej. https://mi-backend.com/api). Sin definir se usa
//   /api, que Next.js (rewrites) o nginx redirigen al backend Django.
export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || '';

export const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || '/api').replace(/\/+$/, '');

/** Construye la URL de un endpoint del backend: apiUrl('games/memory/stats/'). */
export const apiUrl = (endpoint: string) => `${API_BASE_URL}/${endpoint.replace(/^\/+/, '')}`;
