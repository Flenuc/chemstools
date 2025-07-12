'use client';
import { useState } from 'react';

export default function MolecularWeightCalculator() {
  const [formula, setFormula] = useState('H2O');
  type ResultType = { formula: string; molecular_weight: number } | null;
  const [result, setResult] = useState<ResultType>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/calculate/molecular-weight/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ formula }),
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Ocurrió un error.');
      }
    } catch (err) {
      setError('No se pudo conectar con el servidor.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg shadow-md bg-white mt-4">
      <h2 className="text-lg font-semibold mb-2">Calculadora de Peso Molecular</h2>
      <form onSubmit={handleSubmit}>
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={formula}
            onChange={(e) => setFormula(e.target.value)}
            placeholder="Ej: C6H12O6"
            className="flex-grow p-2 border rounded-md"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 font-semibold text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-black-400"
          >
            {isLoading ? 'Calculando...' : 'Calcular'}
          </button>
        </div>
      </form>
      {result && (
        <div className="mt-4 p-3 bg-green-100 border-l-4 border-green-500 text-green-800 rounded-r-lg">
          <p>
            El peso molecular de <strong>{result.formula}</strong> es:{' '}
            <strong className="text-xl">{result.molecular_weight.toFixed(4)} g/mol</strong>
          </p>
        </div>
      )}
      {error && (
        <div className="mt-4 p-3 bg-red-100 border-l-4 border-red-500 text-red-800 rounded-r-lg">
          <p>Error: {error}</p>
        </div>
      )}
    </div>
  );
}