
'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Form, Input, Button } from 'antd';
import { motion } from 'framer-motion';
import { addMolecule } from '../../store/moleculesSlice';
import { addNotification } from '../../store/notificationsSlice';
import { api } from '../../services/api';
import { logTelemetryEvent } from '@/services/telemetryService';

export default function AddMoleculeForm() {
  const [form] = Form.useForm();
  const [isLoading, setIsLoading] = useState(false);
  const dispatch = useDispatch();

  const handleSubmit = async (values: { name: string; structure: string }) => {
    setIsLoading(true);
    try {
      const newMolecule = await api.post('molecules/', { name: values.name, structure_data: values.structure, format: 'SMILES' });
      dispatch(addMolecule(newMolecule));
      logTelemetryEvent('molecule_created', values);
      dispatch(addNotification({ message: `Molécula \"${values.name}\" guardada.`, type: 'success' }));
      form.resetFields();
    } catch (err: any) {
      dispatch(addNotification({ message: err.message || 'Error al guardar.', type: 'error' }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <Form form={form} onFinish={handleSubmit} layout="vertical" className="p-4 border rounded-lg bg-white shadow-sm space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Añadir Nueva Molécula</h3>
        <Form.Item
          name="name"
          label={<span className="text-gray-900">Nombre</span>}
          rules={[{ required: true, message: 'Por favor, introduce el nombre de la molécula.' }]}
        >
          <Input className="w-full p-2 border rounded mt-1 text-gray-900" />
        </Form.Item>
        <Form.Item
          name="structure"
          label={<span className="text-gray-900">Estructura (SMILES)</span>}
          rules={[{ required: true, message: 'Por favor, introduce la estructura en formato SMILES.' }]}
        >
          <Input className="w-full p-2 border rounded mt-1 text-gray-900" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={isLoading} className="w-full">
            {isLoading ? 'Guardando...' : 'Guardar Molécula'}
          </Button>
        </Form.Item>
      </Form>
    </motion.div>
  );
}
