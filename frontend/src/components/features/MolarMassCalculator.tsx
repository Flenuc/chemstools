'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { addNotification } from '@/store/notificationsSlice';
import apiService from '@/services/api';

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
      // Usamos el endpoint que ya existía
      const data = await apiService('calculate/molecular-weight/', {
        method: 'POST',
        body: JSON.stringify({ formula }),
      });
      setResult(data.molecular_weight);
    } catch (err: any) {
      dispatch(addNotification({ message: err.message, type: 'error' }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="card">
      <h2 className="card-title">Calculadora de Masa Molar</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Fórmula Química:</label>
          <input
            type="text"
            value={formula}
            onChange={(e) => setFormula(e.target.value)}
            placeholder="Ej: C6H12O6"
            className="w-full p-2 border rounded mt-1"
          />
        </div>
        <button type="submit" disabled={isLoading} className="w-full p-2 bg-teal-600 text-white rounded hover:bg-teal-700 disabled:bg-gray-400">
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