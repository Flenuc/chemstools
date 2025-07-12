import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface FilterState {
  selectedElementSymbol: string | null;
}

const initialState: FilterState = {
  selectedElementSymbol: null,
};

const filterSlice = createSlice({
  name: 'filters',
  initialState,
  reducers: {
    setElementFilter(state, action: PayloadAction<string | null>) {
      state.selectedElementSymbol = action.payload;
    },
  },
});

export const { setElementFilter } = filterSlice.actions;
export default filterSlice.reducer;