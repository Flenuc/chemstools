import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiService from '@/services/api';

export interface Molecule {
  id: number;
  name: string;
  structure_data: string;
  format: string;
}

// Definimos el tipo para la respuesta paginada de la API
interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Molecule[];
}

interface MoleculesState {
  items: Molecule[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

const initialState: MoleculesState = {
  items: [],
  status: 'idle',
  error: null,
};

// Thunk asíncrono para obtener las moléculas
export const fetchMolecules = createAsyncThunk('molecules/fetchMolecules', async () => {
  // El servicio ahora devolverá el objeto de paginación completo
  const response = await apiService('molecules/');
  // Devolvemos solo el array de resultados para que el reducer lo maneje
  return (response as PaginatedResponse).results;
});

// Thunk para eliminar una molécula 
export const deleteMolecule = createAsyncThunk(
  'molecules/deleteMolecule',
  async (moleculeId: number) => {
    await apiService(`molecules/${moleculeId}/`, { method: 'DELETE' });
    return moleculeId; // Devolvemos el ID para saber cuál eliminar del estado
  }
);

// Thunk para actualizar una molécula 
export const updateMolecule = createAsyncThunk(
  'molecules/updateMolecule',
  async (molecule: Molecule) => {
    const response = await apiService(`molecules/${molecule.id}/`, {
      method: 'PUT', // o 'PATCH' si solo actualizas algunos campos
      body: JSON.stringify(molecule),
    });
    return response as Molecule;
  }
);

const moleculesSlice = createSlice({
  name: 'molecules',
  initialState,
  reducers: {
    addMolecule: (state, action: PayloadAction<Molecule>) => {
      // Añade la nueva molécula al principio de la lista para una mejor UX
      state.items.unshift(action.payload);
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMolecules.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchMolecules.fulfilled, (state, action: PayloadAction<Molecule[]>) => {
        state.status = 'succeeded';
        // Ahora action.payload es el array de moléculas, como se esperaba
        state.items = action.payload;
      })
      .addCase(fetchMolecules.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || null;
      })

          // Manejar la eliminación 
      .addCase(deleteMolecule.fulfilled, (state, action: PayloadAction<number>) => {
        state.items = state.items.filter(mol => mol.id !== action.payload);
      })

        // Manejar la actualización 
      .addCase(updateMolecule.fulfilled, (state, action: PayloadAction<Molecule>) => {
        const index = state.items.findIndex(mol => mol.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      });
  },
});

export const { addMolecule } = moleculesSlice.actions;
export default moleculesSlice.reducer;