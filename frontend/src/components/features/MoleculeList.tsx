'use client';
import { useEffect, useState, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { fetchMolecules, Molecule, deleteMolecule, updateMolecule } from '../../store/moleculesSlice';
import { List, Button, Popconfirm, Modal, Input, Form } from 'antd';
import { motion } from 'framer-motion';

export default function MoleculeList() {
  const dispatch = useDispatch<AppDispatch>();
  const { items = [], status, error } = useSelector((state: RootState) => state.molecules);
  const { selectedElementSymbol } = useSelector((state: RootState) => state.filters);
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingMolecule, setEditingMolecule] = useState<Molecule | null>(null);
  const [form] = Form.useForm();

  const filteredMolecules = useMemo(() => {
    if (!selectedElementSymbol) {
      return items ?? [];
    }
    const regex = new RegExp(selectedElementSymbol, 'i');
    return (items ?? []).filter(mol => regex.test(mol.structure_data));
  }, [items, selectedElementSymbol]);

  const handleDelete = (id: number) => {
    dispatch(deleteMolecule(id));
  };

  const showEditModal = (molecule: Molecule) => {
    setEditingMolecule(molecule);
    form.setFieldsValue(molecule);
    setIsModalVisible(true);
  };

  const handleUpdate = (values: { name: string; structure_data: string }) => {
    if (editingMolecule) {
      dispatch(updateMolecule({ ...editingMolecule, ...values }));
      setIsModalVisible(false);
      setEditingMolecule(null);
    }
  };

  useEffect(() => {
    if (isAuthenticated && status === 'idle') {
      dispatch(fetchMolecules());
    }
  }, [status, dispatch, isAuthenticated]);

  if (status === 'loading') return <p>Cargando moléculas...</p>;
  if (status === 'failed') return <p className="text-red-500">Error al cargar las moléculas: {error}</p>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }} className="p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {selectedElementSymbol ? `Moléculas que contienen ${selectedElementSymbol}` : 'Mis Moléculas'}
      </h3>
      <List
        itemLayout="horizontal"
        dataSource={filteredMolecules}
        renderItem={(mol: Molecule) => (
          <List.Item
            actions={[
              <Button type="link" onClick={() => showEditModal(mol)}>Editar</Button>,
              <Popconfirm title="¿Seguro de eliminar?" onConfirm={() => handleDelete(mol.id)}>
                <Button type="link" danger>Eliminar</Button>
              </Popconfirm>,
            ]}
          >
            <List.Item.Meta
              title={<span className="text-gray-900">{mol.name}</span>}
              description={`${mol.format}: ${mol.structure_data}`}
            />
          </List.Item>
        )}
      />
      <Modal
        title="Editar Molécula"
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
      >
        {editingMolecule && (
          <Form form={form} layout="vertical" onFinish={handleUpdate} initialValues={editingMolecule}>
            <Form.Item name="name" label="Nombre" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="structure_data" label="Estructura (SMILES)" rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Button type="primary" htmlType="submit">Guardar Cambios</Button>
          </Form>
        )}
      </Modal>
    </motion.div>
  );
}
