'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Form, Input, Button, Card, Spin, Alert } from 'antd';
import { motion } from 'framer-motion';
import { addNotification } from '@/store/notificationsSlice';
import { api } from '@/services/api';
import { logTelemetryEvent } from '@/services/telemetryService';

export default function MolarMassCalculator() {
  const [form] = Form.useForm();
  const [result, setResult] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [formula, setFormula] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = async (values: { formula: string }) => {
    setIsLoading(true);
    setResult(null);
    setFormula(values.formula);
    try {
      const data = await api.post('calculate/molecular-weight/', { formula: values.formula });
      logTelemetryEvent('molar_mass_calculated', { formula: values.formula });
      setResult(data.molecular_weight);
    } catch (err: any) {
      dispatch(addNotification({ message: err.message, type: 'error' }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
      <Card title="Calculadora de Masa Molar" className="shadow-lg">
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          <Form.Item
            name="formula"
            label="Fórmula Química"
            initialValue="H2O"
            rules={[{ required: true, message: 'Por favor, introduce una fórmula química.' }]}
          >
            <Input placeholder="Ej: C6H12O6" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={isLoading} block>
              {isLoading ? 'Calculando...' : 'Calcular'}
            </Button>
          </Form.Item>
        </Form>
        {isLoading && <div className="text-center mt-4"><Spin /></div>}
        {result !== null && (
          <Alert
            message={`Masa Molar de ${formula}:`}
            description={`${result.toFixed(4)} g/mol`}
            type="success"
            showIcon
            className="mt-4"
          />
        )}
      </Card>
    </motion.div>
  );
}
