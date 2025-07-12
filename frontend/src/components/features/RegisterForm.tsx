'use client';
import { useState } from 'react';
import apiService from '@/services/api';

export default function RegisterForm() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await apiService('auth/register/', {
        method: 'POST',
        body: JSON.stringify({ username, email, password }),
      });
      setSuccess('¡Usuario registrado con éxito! Ahora puedes iniciar sesión.');
      setUsername('');
      setEmail('');
      setPassword('');
    } catch (err: any) {
      setError(err.message || 'Error al registrar el usuario.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-xl font-bold">Registrarse</h2>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {success && <p className="text-green-500 text-sm">{success}</p>}
      <div>
        <label className="block text-sm font-medium text-black-700">Usuario:</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full p-2 border rounded mt-1" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-black-700">Email:</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-2 border rounded mt-1" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-black-700">Contraseña:</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-2 border rounded mt-1" required />
      </div>
      <button type="submit" className="w-full p-2 bg-green-600 text-white rounded hover:bg-green-700">Registrar</button>
    </form>
  );
}