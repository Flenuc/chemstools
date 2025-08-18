import { api } from './api';

// Generamos un ID de sesión simple para agrupar eventos
const sessionId = Date.now().toString(36) + Math.random().toString(36).substring(2);

/**
 * Envía un evento de telemetría al backend.
 * Es una función "fire-and-forget" para no impactar la UX.
 * @param eventName - El nombre del evento (ej. 'login_success').
 * @param details - Un objeto con datos adicionales.
 */
export const logTelemetryEvent = (eventName: string, details: object = {}) => {
  // Enviamos directamente el objeto, no necesitamos JSON.stringify
  // ya que api.post lo maneja internamente
  api.post('telemetry/log/', {
    event_name: eventName,
    details,
    session_id: sessionId,
  }).catch(error => {
    // No hacemos nada si falla, para no interrumpir al usuario.
    console.warn('Failed to log telemetry event:', error);
  });
};
