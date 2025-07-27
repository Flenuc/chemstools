'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { setTokens, setUser } from '@/store/authSlice';
import { api } from '@/services/api'; // FIX: Import 'api' object instead of default
import { logTelemetryEvent } from '@/services/telemetryService';

export default function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      // FIX: Use api.post for the token request
      const tokenData = await api.post('auth/token/', { username, password });
      dispatch(setTokens(tokenData));

      // FIX: Use api.get for the user data request, passing headers in options
      const userData = await api.get('auth/me/', {
        headers: { Authorization: `Bearer ${tokenData.access}` },
      });
      logTelemetryEvent('login_success', { username });
      dispatch(setUser(userData));
    } catch (err: any) {
      logTelemetryEvent('login_failed', { username, error: err.message });
      setError(err.message || 'Error al iniciar sesión');
    }
  };

  return (
    <div className="bg-white p-8 border rounded-xl shadow-lg space-y-6">
      <h2 className="text-2xl font-bold text-gray-900 text-center">Iniciar Sesión</h2>
      {error && <p className="text-red-600 text-sm text-center">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Usuario</label>
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Contraseña</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900" />
        </div>
        <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          Login
        </button>
      </form>
    </div>
  );
}