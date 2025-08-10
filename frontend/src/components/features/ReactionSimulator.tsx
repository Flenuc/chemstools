// components/features/ReactionSimulator.tsx
'use client';

import React, { useState } from 'react';
import axios from 'axios';

// Tipos TypeScript para la API
interface BalanceEquationRequest {
  equation: string;
}

interface BalanceEquationResponse {
  success: boolean;
  original_equation: string;
  balanced_equation: string;
  coefficients: {
    reactants: number[];
    products: number[];
    compounds: Record<string, number>;
  };
  reaction_type: string;
  id?: number;
  error?: string;
}

interface ErrorResponse {
  equation?: string[];
  error?: string;
}

// Estados del componente
type LoadingState = 'idle' | 'loading' | 'success' | 'error';

const ReactionSimulator: React.FC = () => {
  // Estados del componente
  const [equation, setEquation] = useState<string>('');
  const [result, setResult] = useState<BalanceEquationResponse | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Validación de entrada
  const validateEquation = (eq: string): string | null => {
    if (!eq.trim()) {
      return 'Por favor ingresa una ecuación química';
    }
    if (!eq.includes('->')) {
      return 'La ecuación debe contener "->" para separar reactivos y productos';
    }
    const parts = eq.split('->');
    if (parts.length !== 2) {
      return 'La ecuación debe tener exactamente un "->" separando reactivos y productos';
    }
    if (!parts[0].trim() || !parts[1].trim()) {
      return 'Tanto reactivos como productos deben estar presentes';
    }
    return null;
  };

  // Función para balancear la ecuación
  const handleBalanceEquation = async () => {
    // Validar entrada
    const validationError = validateEquation(equation);
    if (validationError) {
      setErrorMessage(validationError);
      setLoadingState('error');
      return;
    }

    // Iniciar carga
    setLoadingState('loading');
    setErrorMessage('');
    setResult(null);

    try {
      const requestData: BalanceEquationRequest = {
        equation: equation.trim()
      };

      const response = await axios.post<BalanceEquationResponse>(
        '/api/reactions/balance-equation/',
        requestData,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setResult(response.data);
        setLoadingState('success');
      } else {
        setErrorMessage(response.data.error || 'Error desconocido al balancear la ecuación');
        setLoadingState('error');
      }
    } catch (error) {
      console.error('Error al balancear ecuación:', error);
      
      if (axios.isAxiosError(error)) {
        if (error.response?.data) {
          const errorData = error.response.data as ErrorResponse;
          if (errorData.equation) {
            setErrorMessage(errorData.equation[0]);
          } else if (errorData.error) {
            setErrorMessage(errorData.error);
          } else {
            setErrorMessage('Error del servidor al procesar la ecuación');
          }
        } else if (error.request) {
          setErrorMessage('No se pudo conectar con el servidor. Verifica tu conexión.');
        } else {
          setErrorMessage('Error inesperado al procesar la solicitud');
        }
      } else {
        setErrorMessage('Error inesperado al procesar la ecuación');
      }
      
      setLoadingState('error');
    }
  };

  // Función para limpiar resultados
  const handleClear = () => {
    setEquation('');
    setResult(null);
    setLoadingState('idle');
    setErrorMessage('');
  };

  // Función para manejar el envío del formulario
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleBalanceEquation();
  };

  // Ejemplos predefinidos
  const examples = [
    { label: 'Síntesis', equation: 'H2 + O2 -> H2O' },
    { label: 'Descomposición', equation: 'H2O2 -> H2O + O2' },
    { label: 'Combustión', equation: 'CH4 + O2 -> CO2 + H2O' }
  ];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Simulador de Reacciones Químicas
        </h1>
        <p className="text-gray-600">
          Ingresa una ecuación química y obtendrás la versión balanceada con sus coeficientes
        </p>
      </div>

      {/* Formulario de entrada */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="equation" className="block text-sm font-medium text-gray-700 mb-2">
              Ecuación Química (usa '-' y '&gt;' para separar reactivos y productos)
            </label>
            <input
              id="equation"
              type="text"
              value={equation}
              onChange={(e) => setEquation(e.target.value)}
              placeholder="Ej: H2 + O2 -> H2O"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-lg font-mono"
              disabled={loadingState === 'loading'}
            />
          </div>

          {/* Ejemplos rápidos */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-500">Ejemplos:</span>
            {examples.map((example, index) => (
              <button
                key={index}
                type="button"
                onClick={() => setEquation(example.equation)}
                className="text-sm px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors text-blue-600 hover:text-blue-800"
                disabled={loadingState === 'loading'}
              >
                {example.label}
              </button>
            ))}
          </div>

          {/* Botones de acción */}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={!equation.trim() || loadingState === 'loading'}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 px-6 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {loadingState === 'loading' ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                  Balanceando...
                </div>
              ) : (
                'Balancear Ecuación'
              )}
            </button>
            
            <button
              type="button"
              onClick={handleClear}
              className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              disabled={loadingState === 'loading'}
            >
              Limpiar
            </button>
          </div>
        </form>
      </div>

      {/* Mensaje de error */}
      {loadingState === 'error' && errorMessage && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="text-sm text-red-700 mt-1">{errorMessage}</p>
            </div>
          </div>
        </div>
      )}

      {/* Resultados */}
      {loadingState === 'success' && result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-green-800 ml-2">¡Ecuación Balanceada!</h3>
          </div>

          <div className="space-y-4">
            {/* Ecuación original */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Ecuación Original:</h4>
              <p className="text-lg font-mono bg-gray-100 px-3 py-2 rounded border">
                {result.original_equation}
              </p>
            </div>

            {/* Ecuación balanceada */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-1">Ecuación Balanceada:</h4>
              <p className="text-xl font-mono bg-white px-4 py-3 rounded border-2 border-green-300 text-green-800 font-semibold">
                {result.balanced_equation}
              </p>
            </div>

            {/* Información adicional */}
            <div className="grid md:grid-cols-2 gap-4">
              {/* Tipo de reacción */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Tipo de Reacción:</h4>
                <p className="capitalize bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium inline-block">
                  {result.reaction_type}
                </p>
              </div>

              {/* Coeficientes */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Coeficientes:</h4>
                <div className="space-y-1 text-sm">
                  <p>
                    <span className="font-medium">Reactivos:</span> [{result.coefficients.reactants.join(', ')}]
                  </p>
                  <p>
                    <span className="font-medium">Productos:</span> [{result.coefficients.products.join(', ')}]
                  </p>
                </div>
              </div>
            </div>

            {/* Detalles de coeficientes por compuesto */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Coeficientes por Compuesto:</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                {Object.entries(result.coefficients.compounds).map(([compound, coefficient]) => (
                  <div key={compound} className="bg-gray-100 px-3 py-2 rounded text-center">
                    <p className="font-mono text-sm text-gray-600">{compound}</p>
                    <p className="font-bold text-lg text-gray-800">{coefficient}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Instrucciones */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-blue-800 mb-2">💡 Instrucciones de Uso</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Usa el formato: <code className="bg-blue-100 px-1 rounded">Reactivos -&gt; Productos</code></li>
          <li>• Separa múltiples compuestos con <code className="bg-blue-100 px-1 rounded">+</code></li>
          <li>• Ejemplos: <code className="bg-blue-100 px-1 rounded">H2 + O2 -&gt; H2O</code> o <code className="bg-blue-100 px-1 rounded">CH4 + O2 -&gt; CO2 + H2O</code></li>
          <li>• El sistema detecta automáticamente el tipo de reacción</li>
        </ul>
      </div>
    </div>
  );
};

export default ReactionSimulator;