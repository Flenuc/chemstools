'use client';
import { useState, useEffect } from 'react';

export default function HealthCheck() {
  const [backendStatus, setBackendStatus] = useState('pending');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health/');
        if (response.ok) {
          const data = await response.json();
          setBackendStatus(data.status);
        } else {
          setBackendStatus('error');
        }
      } catch (error) {
        setBackendStatus('error');
      }
    };
    checkStatus();
  }, []);

  return (
    <div className="p-4 border rounded-lg shadow-md bg-white">
      <h2 className="text-lg font-semibold mb-2">Estado del Sistema</h2>
      <div className="flex items-center space-x-2">
        <span>Backend:</span>
        {backendStatus === 'ok' && <span className="px-2 py-1 text-xs font-bold text-green-800 bg-green-200 rounded-full">Online</span>}
        {backendStatus === 'pending' && <span className="px-2 py-1 text-xs font-bold text-yellow-800 bg-yellow-200 rounded-full">Verificando...</span>}
        {backendStatus === 'error' && <span className="px-2 py-1 text-xs font-bold text-red-800 bg-red-200 rounded-full">Offline</span>}
      </div>
    </div>
  );
}
