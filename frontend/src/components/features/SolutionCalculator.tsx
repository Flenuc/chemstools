"use client";

import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '@/store';
import { setSolutionInput, resetSolutionForm } from '@/store/calculatorsSlice';
import { api } from '@/services/api';
import Card from '@/components/common/Card';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';

interface SolutionResult {
  percent_mass_mass: string;
  percent_mass_volume: string;
}

const SolutionCalculator = () => {
  const dispatch = useDispatch<AppDispatch>();
  const formState = useSelector((state: RootState) => state.calculators);
  const [result, setResult] = useState<SolutionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof typeof formState, value: string) => {
    dispatch(setSolutionInput({ field, value }));
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      solute_mass: formState.soluteMass || null,
      solvent_mass: formState.solventMass || null,
      solution_volume: formState.solutionVolume || null,
      density: formState.density || null,
    };

    try {
      const response = await api.post('calculators/solution-calculator/', payload);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Error en el cálculo. Revise los datos ingresados.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleReset = () => {
    dispatch(resetSolutionForm());
    setResult(null);
    setError(null);
  };

  return (
    <Card title="Calculadora de Disoluciones">
      <div className="space-y-4 text-gray-900">
        <p className="text-sm text-gray-600">Introduce al menos dos valores para calcular. La densidad es opcional pero ayuda a convertir entre %m/m y %m/v.</p>
        <Input
          id="soluteMass"
          label="Masa del Soluto (g)"
          type="number"
          value={formState.soluteMass}
          onChange={(e) => handleInputChange('soluteMass', e.target.value)}
          placeholder="e.g., 10"
        />
        <Input
          id="solventMass"
          label="Masa del Disolvente (g)"
          type="number"
          value={formState.solventMass}
          onChange={(e) => handleInputChange('solventMass', e.target.value)}
          placeholder="e.g., 90"
        />
        <Input
          id="solutionVolume"
          label="Volumen de la Disolución (mL)"
          type="number"
          value={formState.solutionVolume}
          onChange={(e) => handleInputChange('solutionVolume', e.target.value)}
          placeholder="e.g., 100"
        />
        <Input
          id="density"
          label="Densidad de la Disolución (g/mL)"
          type="number"
          value={formState.density}
          onChange={(e) => handleInputChange('density', e.target.value)}
          placeholder="e.g., 1.1"
        />
        <div className="flex space-x-2">
          <Button onClick={handleCalculate} isLoading={loading} className="flex-1">
            Calcular
          </Button>
          <Button onClick={handleReset} variant="secondary" className="flex-1">
            Limpiar
          </Button>
        </div>
        
        {error && <p className="text-red-500">{error}</p>}

        {result && (
          <div className="mt-4 p-4 bg-gray-100 rounded-lg space-y-2 text-gray-900">
            <h3 className="font-semibold">Resultados:</h3>
            <p><strong>% Masa/Masa:</strong> {result.percent_mass_mass} %</p>
            <p><strong>% Masa/Volumen:</strong> {result.percent_mass_volume} %</p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default SolutionCalculator;