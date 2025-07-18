'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { addNotification } from '@/store/notificationsSlice';
import apiService from '@/services/api';
import { logTelemetryEvent } from '@/services/telemetryService';

export default function MolarMassCalculator() {
  const [formula, setFormula] = useState('H2O');
  const [result, setResult] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResult(null);
    try {
      const data = await apiService('calculate/molecular-weight/', {
        method: 'POST',
        body: JSON.stringify({ formula }),
      });
      logTelemetryEvent('molar_mass_calculated', { formula });
      setResult(data.molecular_weight);
    } catch (err: any) {
      dispatch(addNotification({ message: err.message, type: 'error' }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 border rounded-xl shadow-lg">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Calculadora de Masa Molar</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Fórmula Química:</label>
          <input
            type="text"
            value={formula}
            onChange={(e) => setFormula(e.target.value)}
            placeholder="Ej: C6H12O6"
            className="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-teal-500 focus:border-teal-500"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-teal-600 hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500 disabled:bg-gray-400"
        >
          {isLoading ? 'Calculando...' : 'Calcular'}
        </button>
      </form>
      {result !== null && (
        <div className="mt-4 p-3 bg-blue-100 border-l-4 border-blue-500 text-blue-800 rounded-r-lg">
          <p>
            Masa Molar de <strong>{formula}</strong>: <strong className="text-xl">{result.toFixed(4)} g/mol</strong>
          </p>
        </div>
      )}
    </div>
  );
}