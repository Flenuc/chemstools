'use client';

import { useState } from 'react';
import { ConfigProvider } from 'antd';
import { theme } from '@/lib/theme';

export default function TestRegisterPage() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted with data:', formData);
    
    setLoading(true);
    setError('');
    setResponse(null);

    try {
      // Validaciones básicas
      if (formData.password !== formData.confirmPassword) {
        throw new Error('Las contraseñas no coinciden');
      }

      const res = await fetch('/api/auth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        })
      });

      const data = await res.json();
      console.log('Response:', data);

      if (res.ok) {
        setResponse(data);
        alert('¡Registro exitoso! Usuario: ' + data.username);
      } else {
        setError(JSON.stringify(data));
      }
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message || 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ConfigProvider theme={theme}>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 p-8">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h1 className="text-2xl font-bold mb-4">Test de Registro (Simple HTML Form)</h1>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Password</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Confirm Password</label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Registrando...' : 'Registrar'}
              </button>
            </form>

            {error && (
              <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                <strong>Error:</strong> {error}
              </div>
            )}

            {response && (
              <div className="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                <strong>Éxito:</strong> Usuario {response.username} registrado con ID {response.id}
              </div>
            )}

            <div className="mt-6 p-4 bg-gray-100 rounded">
              <h3 className="font-bold mb-2">Debug Info:</h3>
              <pre className="text-xs overflow-auto">
                {JSON.stringify({ formData, response, error, loading }, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </ConfigProvider>
  );
}
