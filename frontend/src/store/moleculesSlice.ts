import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import apiService from '../services/api';

export interface Molecule {
  id: number;
  name: string;
  structure_data: string;
  format: string;
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

export const fetchMolecules = createAsyncThunk('molecules/fetchMolecules', async () => {
  const response = await apiService('molecules/');
  return response as Molecule[];
});

const moleculesSlice = createSlice({
  name: 'molecules',
  initialState,
  reducers: {
    addMolecule: (state, action: PayloadAction<Molecule>) => {
      state.items.push(action.payload);
    },
    resetStatus: (state) => {
      state.status = 'idle';
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMolecules.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchMolecules.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload;
      })
      .addCase(fetchMolecules.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || null;
      });
  },
});

export const { addMolecule, resetStatus } = moleculesSlice.actions;
export default moleculesSlice.reducer;