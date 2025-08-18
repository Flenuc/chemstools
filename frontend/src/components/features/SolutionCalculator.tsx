"use client";

import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '@/store';
import { setSolutionInput, resetSolutionForm } from '@/store/calculatorsSlice';
import { addNotification } from '@/store/notificationsSlice';
import { api } from '@/services/api';
import { Card, Form, InputNumber, Button, Alert, Space, Typography } from 'antd';
import { motion } from 'framer-motion';

const { Text } = Typography;

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
  const [form] = Form.useForm();

  const handleInputChange = (field: keyof typeof formState, value: number | null) => {
    dispatch(setSolutionInput({ field, value: value?.toString() || '' }));
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    const values = form.getFieldsValue();
    const payload = {
      solute_mass: values.soluteMass || null,
      solvent_mass: values.solventMass || null,
      solution_volume: values.solutionVolume || null,
      density: values.density || null,
    };

    try {
      const response = await api.post('calculators/solution-calculator/', payload);
      setResult(response);
      dispatch(addNotification({ message: 'Cálculo de disolución exitoso.', type: 'success' }));
    } catch (err: any) {
      const errorMessage = err.message || 'Error en el cálculo. Revise los datos ingresados.';
      setError(errorMessage);
      dispatch(addNotification({ message: errorMessage, type: 'error' }));
    } finally {
      setLoading(false);
    }
  };
  
  const handleReset = () => {
    dispatch(resetSolutionForm());
    form.resetFields();
    setResult(null);
    setError(null);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <Card title="Calculadora de Disoluciones" className="shadow-lg">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Text type="secondary">
            Introduce al menos dos valores para calcular. La densidad es opcional pero ayuda a convertir entre %m/m y %m/v.
          </Text>
          <Form form={form} layout="vertical">
            <Form.Item
              name="soluteMass"
              label="Masa del Soluto (g)"
            >
              <InputNumber
                placeholder="e.g., 10"
                style={{ width: '100%' }}
                onChange={(value) => handleInputChange('soluteMass', value)}
              />
            </Form.Item>
            <Form.Item
              name="solventMass"
              label="Masa del Disolvente (g)"
            >
              <InputNumber
                placeholder="e.g., 90"
                style={{ width: '100%' }}
                onChange={(value) => handleInputChange('solventMass', value)}
              />
            </Form.Item>
            <Form.Item
              name="solutionVolume"
              label="Volumen de la Disolución (mL)"
            >
              <InputNumber
                placeholder="e.g., 100"
                style={{ width: '100%' }}
                onChange={(value) => handleInputChange('solutionVolume', value)}
              />
            </Form.Item>
            <Form.Item
              name="density"
              label="Densidad de la Disolución (g/mL)"
            >
              <InputNumber
                placeholder="e.g., 1.1"
                style={{ width: '100%' }}
                onChange={(value) => handleInputChange('density', value)}
              />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" onClick={handleCalculate} loading={loading}>
                  Calcular
                </Button>
                <Button onClick={handleReset}>
                  Limpiar
                </Button>
              </Space>
            </Form.Item>
          </Form>
          
          {error && <Alert message={error} type="error" showIcon />}

          {result && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
              <Alert
                message="Resultados"
                description={
                  <Space direction="vertical">
                    <Text><strong>% Masa/Masa:</strong> {result.percent_mass_mass} %</Text>
                    <Text><strong>% Masa/Volumen:</strong> {result.percent_mass_volume} %</Text>
                  </Space>
                }
                type="success"
                showIcon
              />
            </motion.div>
          )}
        </Space>
      </Card>
    </motion.div>
  );
};

export default SolutionCalculator;
