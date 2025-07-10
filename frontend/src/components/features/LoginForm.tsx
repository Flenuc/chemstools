'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { setTokens, setUser } from '@/store/authSlice';
import apiService from '@/services/api';

export default function LoginForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const tokenData = await apiService('auth/token/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      dispatch(setTokens(tokenData));

      const userData = await apiService('auth/me/', {
        headers: { Authorization: `Bearer ${tokenData.access}` },
      });
      dispatch(setUser(userData));
    } catch (err: any) {
      setError(err.message || 'Error al iniciar sesión');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-xl font-bold">Iniciar Sesión</h2>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <div>
        <label className="block text-sm font-medium text-gray-700">Usuario:</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full p-2 border rounded mt-1" />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Contraseña:</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-2 border rounded mt-1" />
      </div>
      <button type="submit" className="w-full p-2 bg-blue-600 text-white rounded hover:bg-blue-700">Login</button>
    </form>
  );
}