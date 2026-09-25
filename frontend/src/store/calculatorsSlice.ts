import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SolutionState {
  soluteMass: string;
  solventMass: string;
  solutionVolume: string;
  density: string;
}

const initialState: SolutionState = {
  soluteMass: '',
  solventMass: '',
  solutionVolume: '',
  density: '',
};

const calculatorsSlice = createSlice({
  name: 'calculators',
  initialState,
  reducers: {
    setSolutionInput(state, action: PayloadAction<{ field: keyof SolutionState; value: string }>) {
      state[action.payload.field] = action.payload.value;
    },
    resetSolutionForm(state) {
      return initialState;
    },
  },
});

export const { setSolutionInput, resetSolutionForm } = calculatorsSlice.actions;
export default calculatorsSlice.reducer;