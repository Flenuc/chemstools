import apiService from './api';

// Generamos un ID de sesión simple para agrupar eventos
const sessionId = Date.now().toString(36) + Math.random().toString(36).substring(2);

/**
 * Envía un evento de telemetría al backend.
 * Es una función "fire-and-forget" para no impactar la UX.
 * @param eventName - El nombre del evento (ej. 'login_success').
 * @param details - Un objeto con datos adicionales.
 */
export const logTelemetryEvent = (eventName: string, details: object = {}) => {
  apiService('telemetry/log/', {
    method: 'POST',
    body: JSON.stringify({
      event_name: eventName,
      details,
      session_id: sessionId,
    }),
  }).catch(error => {
    // No hacemos nada si falla, para no interrumpir al usuario.
    console.warn('Failed to log telemetry event:', error);
  });
};