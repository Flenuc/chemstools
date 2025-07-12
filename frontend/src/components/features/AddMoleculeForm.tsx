'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { addMolecule } from '../../store/moleculesSlice';
import apiService from '../../services/api';

export default function AddMoleculeForm() {
  const [name, setName] = useState('');
  const [structure, setStructure] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const dispatch = useDispatch();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const newMolecule = await apiService('molecules/', {
        method: 'POST',
        body: JSON.stringify({ name, structure_data: structure, format: 'SMILES' }),
      });
      dispatch(addMolecule(newMolecule));
      setName('');
      setStructure('');
    } catch (err: any) {
      setError(err.message || 'Error al guardar la molécula.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded-lg bg-white shadow-sm space-y-4">
      <h3 className="text-lg font-semibold">Añadir Nueva Molécula</h3>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      {/* ... (inputs) */}
      <button type="submit" disabled={isLoading} className="w-full p-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:bg-gray-400">
        {isLoading ? 'Guardando...' : 'Guardar Molécula'}
      </button>
    </form>
  );
}