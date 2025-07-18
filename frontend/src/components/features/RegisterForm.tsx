'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import apiService from '@/services/api';
import { addNotification } from '@/store/notificationsSlice';

export default function RegisterForm() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await apiService('auth/register/', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      });
      dispatch(addNotification({ message: '¡Usuario registrado con éxito!', type: 'success' }));
      setUsername('');
      setEmail('');
      setPassword('');
    } catch (err: any) {
      dispatch(addNotification({ message: err.message || 'Error al registrar.', type: 'error' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-2xl font-bold text-gray-900 text-center">Registrarse</h2>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {success && <p className="text-green-500 text-sm">{success}</p>}
      <div>
        <label className="block text-sm font-medium text-gray-900">Usuario:</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-900">Email:</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-900">Contraseña:</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-gray-900" required />
      </div>
      <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">Registrar</button>
    </form>
  );
}