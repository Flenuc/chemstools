'use client';
import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { fetchMolecules, Molecule } from '../../store/moleculesSlice';
import { useMemo } from 'react';

export default function MoleculeList() {
  const dispatch = useDispatch<AppDispatch>();
  const { items = [], status, error } = useSelector((state: RootState) => state.molecules);
  const { selectedElementSymbol } = useSelector((state: RootState) => state.filters);
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

    // Filtra las moléculas basándose en el símbolo seleccionado
  const filteredMolecules = useMemo(() => {
    if (!selectedElementSymbol) {
      return items ?? [];
    }
    const regex = new RegExp(selectedElementSymbol, 'i');
    return (items ?? []).filter(mol => regex.test(mol.structure_data));
  }, [items, selectedElementSymbol]);

  useEffect(() => {
    if (isAuthenticated && status === 'idle') {
      dispatch(fetchMolecules());
    }
  }, [status, dispatch, isAuthenticated]);

  if (status === 'loading') return <p>Cargando moléculas...</p>;
  if (status === 'failed') return <p className="text-red-500">Error al cargar las moléculas: {error}</p>;

  return (
    <div className="space-y-3 p-4 border rounded-lg bg-white shadow-sm">
      <h3 className="text-lg font-semibold">
        {selectedElementSymbol 
          ? `Moléculas que contienen ${selectedElementSymbol}` 
          : 'Mis Moléculas'}
      </h3>
      {filteredMolecules.length === 0 ? (
        <p>No se encontraron moléculas.</p>
      ) : (
        <ul className="divide-y divide-black-200">
          {filteredMolecules.map((mol: Molecule) => (
            <li key={mol.id} className="p-2 hover:bg-black-50">
              {mol.name} ({mol.format}: {mol.structure_data})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
