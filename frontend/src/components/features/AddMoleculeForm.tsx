'use client';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { addMolecule } from '../../store/moleculesSlice';
import { addNotification } from '../../store/notificationsSlice';
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
      dispatch(addNotification({ message: `Molécula "${name}" guardada.`, type: 'success' }));
      setName('');
      setStructure('');
    } catch (err: any) {
      dispatch(addNotification({ message: err.message || 'Error al guardar.', type: 'error' }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 border rounded-lg shadow-sm space-y-4">
      <h3 className="text-xl font-bold text-slate-900 mb-4">Añadir Nueva Molécula</h3>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <div>
        <label className="block text-sm font-medium text-gray-700">Nombre:</label>
        <input
          type="text"
          value={name}
          onChange={e => setName(e.target.value)}
          className="w-full p-2 border rounded mt-1"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700">Estructura (SMILES):</label>
        <input
          type="text"
          value={structure}
          onChange={e => setStructure(e.target.value)}
          className="w-full p-2 border rounded mt-1"
          required
        />
      </div>
      <button type="submit" disabled={isLoading} className="w-full p-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:bg-gray-400">
        {isLoading ? 'Guardando...' : 'Guardar Molécula'}
      </button>
    </form>
  );
}