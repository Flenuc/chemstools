'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { addMolecule } from '../../store/moleculesSlice';
import apiService from '../../services/api';

export default function AddMoleculeForm() {
  const [name, setName] = useState('');
  const [structure, setStructure] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newMolecule = await apiService('molecules/', {
        method: 'POST',
        body: JSON.stringify({ name, structure_data: structure, format: 'SMILES' }),
      });
      dispatch(addMolecule(newMolecule));
      setName('');
      setStructure('');
    } catch (error) {
      console.error("Error al añadir molécula:", error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded-lg bg-white shadow-sm space-y-4">
      <h3 className="text-lg font-semibold">Añadir Nueva Molécula</h3>
      <div>
        <label className="block text-sm font-medium text-gray-700">Nombre:</label>
        <input type="text" value={name} onChange={e => setName(e.target.value)} className="w-full p-2 border rounded mt-1" required />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Estructura (SMILES):</label>
        <input type="text" value={structure} onChange={e => setStructure(e.target.value)} className="w-full p-2 border rounded mt-1" required />
      </div>
      <button type="submit" className="w-full p-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">Guardar Molécula</button>
    </form>
  );
}