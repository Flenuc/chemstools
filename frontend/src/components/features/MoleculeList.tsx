'use client';
import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { fetchMolecules, Molecule } from '../../store/moleculesSlice';

export default function MoleculeList() {
  const dispatch = useDispatch<AppDispatch>();
  const { items, status, error } = useSelector((state: RootState) => state.molecules);
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  useEffect(() => {
    if (isAuthenticated && status === 'idle') {
      dispatch(fetchMolecules());
    }
  }, [status, dispatch, isAuthenticated]);

  if (status === 'loading') return <p>Cargando moléculas...</p>;
  if (status === 'failed') return <p className="text-red-500">Error al cargar las moléculas: {error}</p>;

  return (
    <div className="space-y-3 p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold">Mis Moléculas</h3>
      {items.length === 0 ? (
        <p>No tienes moléculas guardadas.</p>
      ) : (
        <ul className="divide-y divide-black-200">
          {items.map((mol: Molecule) => (
            <li key={mol.id} className="p-2 hover:bg-black-50">
              {mol.name} ({mol.format}: {mol.structure_data})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
