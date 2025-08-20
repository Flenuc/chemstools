import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
// import api from '../../services/api'; // Se importará el servicio de API real

// --- Tipos de Datos (reutilizar/importar desde los componentes) ---

interface CalculationInput {
    mode: 'ph_to_all' | 'concentration_to_ph' | 'buffer' | 'activity_correction';
    [key: string]: any; // Flexible para diferentes modos
}

interface PHCalculationResult {
    ph: number;
    poh: number;
    h_concentration: number;
    oh_concentration: number;
    is_acid: boolean;
    steps: { title: string; explanation: string; formula: string }[];
    warnings: string[];
}

interface PHCalculationHistory {
    key: string;
    calculationType: string;
    inputSummary: string;
    ph: number;
    timestamp: string;
}

interface PHUserStats {
    totalCalculations: number;
    avgCalculationTime: number;
    warningRate: number;
}

interface ChemicalPreset {
    id: string;
    name: string;
    values: Partial<CalculationInput>;
}

interface AdvancedPHState {
    currentCalculation: CalculationInput | null;
    calculationResult: PHCalculationResult | null;
    calculationHistory: PHCalculationHistory[];
    isCalculating: boolean;
    isLoadingHistory: boolean;
    isExporting: boolean;
    selectedPreset: ChemicalPreset | null;
    userStats: PHUserStats | null;
    exportProgress: number;
    errors: Record<string, string | null>;
    warnings: string[];
}

// --- Estado Inicial ---
const initialState: AdvancedPHState = {
    currentCalculation: null,
    calculationResult: null,
    calculationHistory: [],
    isCalculating: false,
    isLoadingHistory: false,
    isExporting: false,
    selectedPreset: null,
    userStats: null,
    exportProgress: 0,
    errors: {},
    warnings: [],
};

// --- Thunks Asíncronos (Simulados) ---

// Simula una llamada a la API
const mockApiCall = (data: any, delay = 500) => new Promise(resolve => setTimeout(() => resolve(data), delay));

export const calculateAdvancedPH = createAsyncThunk<PHCalculationResult, CalculationInput>(
    'advancedPH/calculate',
    async (calculationInput, { rejectWithValue }) => {
        try {
            // const response = await api.post('/calculators/advanced-ph-calculator/', calculationInput);
            // return response.data;
            const mockResponse: PHCalculationResult = {
                ph: 1.0, poh: 13.0, h_concentration: 0.1, oh_concentration: 1e-13, is_acid: true,
                steps: [{ title: 'Mock Step', explanation: 'Mock explanation', formula: 'pH = -log[H+]' }],
                warnings: ['This is a mock warning.'],
            };
            return await mockApiCall(mockResponse) as PHCalculationResult;
        } catch (error: any) {
            return rejectWithValue(error.response.data);
        }
    }
);

export const fetchPHHistory = createAsyncThunk<PHCalculationHistory[], { userId: string; page: number; filters?: any }>(
    'advancedPH/fetchHistory',
    async (params, { rejectWithValue }) => {
        try {
            // const response = await api.get(`/calculators/ph-history/`, { params });
            // return response.data;
            const mockResponse: PHCalculationHistory[] = [
                { key: '1', calculationType: 'concentration_to_ph', inputSummary: 'HCl 0.1M', ph: 1.00, timestamp: new Date().toISOString() },
            ];
            return await mockApiCall(mockResponse) as PHCalculationHistory[];
        } catch (error: any) {
            return rejectWithValue(error.response.data);
        }
    }
);

export const fetchPHStats = createAsyncThunk<PHUserStats, string>(
    'advancedPH/fetchStats',
    async (userId, { rejectWithValue }) => {
        try {
            // const response = await api.get(`/calculators/ph-stats/${userId}`);
            // return response.data;
             const mockResponse: PHUserStats = { totalCalculations: 128, avgCalculationTime: 23, warningRate: 0.15 };
            return await mockApiCall(mockResponse) as PHUserStats;
        } catch (error: any) {
            return rejectWithValue(error.response.data);
        }
    }
);

// --- Slice Definition ---
const advancedPHSlice = createSlice({
    name: 'advancedPH',
    initialState,
    reducers: {
        setCalculationInput: (state, action: PayloadAction<CalculationInput>) => {
            state.currentCalculation = action.payload;
        },
        clearResults: (state) => {
            state.calculationResult = null;
            state.warnings = [];
            state.errors = {};
        },
        setSelectedPreset: (state, action: PayloadAction<ChemicalPreset>) => {
            state.selectedPreset = action.payload;
            // Aseguramos que la fusión de objetos no resulte en un tipo incompatible
            const newCalculation = { ...state.currentCalculation, ...action.payload.values };
            if(newCalculation.mode) { // Chequeo para asegurar que 'mode' no es undefined
                state.currentCalculation = newCalculation as CalculationInput;
            }
        },
        clearErrors: (state) => {
            state.errors = {};
        },
    },
    extraReducers: (builder) => {
        builder
            // Calculate PH
            .addCase(calculateAdvancedPH.pending, (state) => {
                state.isCalculating = true;
                state.calculationResult = null;
                state.errors = {};
            })
            .addCase(calculateAdvancedPH.fulfilled, (state, action) => {
                state.isCalculating = false;
                state.calculationResult = action.payload;
                state.warnings = action.payload.warnings;
            })
            .addCase(calculateAdvancedPH.rejected, (state, action) => {
                state.isCalculating = false;
                state.errors.calculation = action.payload as string;
            })
            // Fetch History
            .addCase(fetchPHHistory.pending, (state) => {
                state.isLoadingHistory = true;
            })
            .addCase(fetchPHHistory.fulfilled, (state, action) => {
                state.isLoadingHistory = false;
                state.calculationHistory = action.payload; // Aquí se podría concatenar para infinite scroll
            })
            .addCase(fetchPHHistory.rejected, (state, action) => {
                state.isLoadingHistory = false;
                state.errors.history = action.payload as string;
            })
            // Fetch Stats
            .addCase(fetchPHStats.fulfilled, (state, action) => {
                state.userStats = action.payload;
            });
    },
});

export const {
    setCalculationInput,
    clearResults,
    setSelectedPreset,
    clearErrors,
} = advancedPHSlice.actions;

export default advancedPHSlice.reducer;
