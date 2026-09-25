"use client";

import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '@/store';
import { addNotification } from '@/store/notificationsSlice';
import { api } from '@/services/api';
import Card from '@/components/common/Card';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';

interface PHResult {
  ph: number;
  poh: number;
  h_concentration: string;
  oh_concentration: string;
}

const PHCalculator = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [inputValue, setInputValue] = useState('');
  const [inputType, setInputType] = useState<'ph' | 'poh' | 'h_concentration' | 'oh_concentration'>('ph');
  const [result, setResult] = useState<PHResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const token = useSelector((state: RootState) => state.auth.accessToken);

  const handleCalculate = async () => {
    if (!token || !inputValue) return;
    setLoading(true);
    setError(null);
    setResult(null);


    try {
      const payload = { [inputType]: parseFloat(inputValue) };
      const response = await api.post('calculators/ph-calculator/', payload);
      setResult(response);
      // Añadir notificación de éxito
      dispatch(addNotification({ message: 'Cálculo realizado con éxito.', type: 'success' }));
    } catch (err: any) {
      const errorMessage = err.message || 'Error en el cálculo. Verifique el valor ingresado.';
      setError(errorMessage);
      // Añadir notificación de error
      dispatch(addNotification({ message: errorMessage, type: 'error' }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="Calculadora de pH/pOH">
      <div className="space-y-4">
        <div className="flex items-end space-x-2">
          <div className="flex-grow text-gray-900">
            <Input
              id="ph-input"
              label={`Valor de ${inputType}`}
              type="number"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={`e.g., 7 para pH`}
            />
          </div>
          <select
            value={inputType}
            onChange={(e) => setInputType(e.target.value as any)}
            className="h-10 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="ph">pH</option>
            <option value="poh">pOH</option>
            <option value="h_concentration">[H+]</option>
            <option value="oh_concentration">[OH-]</option>
          </select>
        </div>
        <Button onClick={handleCalculate} isLoading={loading} disabled={!inputValue}>
          Calcular
        </Button>
        {error && <p className="text-red-500">{error}</p>}
        {result && (
          <div className="mt-4 p-4 bg-gray-100 rounded-lg space-y-2 text-gray-900">
            <h3 className="font-semibold text-gray-900">Resultados:</h3>
            <p><strong>pH:</strong> {result.ph.toFixed(2)}</p>
            <p><strong>pOH:</strong> {result.poh.toFixed(2)}</p>
            <p><strong>[H+]:</strong> {result.h_concentration} M</p>
            <p><strong>[OH-]:</strong> {result.oh_concentration} M</p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default PHCalculator;
