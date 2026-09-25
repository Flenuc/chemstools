import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api'; // USAMOS EL SERVICIO API EXISTENTE
import phCalculatorService from '../services/phCalculatorService';
import {
    CalculationInput,
    PHCalculationResult,
    PHCalculationHistory,
    PHUserStats,
    ChemicalPreset,
    HistoryFilters,
    ExportRequest
} from '../types/advancedPH';
import { RootState } from './index';

// --- Tipos de Estado ---
interface AdvancedPHState {
    currentCalculation: CalculationInput | null;
    calculationResult: PHCalculationResult | null;
    calculationHistory: PHCalculationHistory[];
    historyCount: number;
    historyNext: string | null;
    historyPrevious: string | null;
    isCalculating: boolean;
    isLoadingHistory: boolean;
    isLoadingStats: boolean;
    isLoadingPresets: boolean;
    isLoadingBuffers: boolean;
    isExporting: boolean;
    selectedPreset: ChemicalPreset | null;
    presets: any[];
    presetCategories: any[];
    bufferSystems: any[];
    bufferSuggestions: any[];
    userStats: any | null;
    exportProgress: number;
    errors: Record<string, any | null>;
    warnings: any[];
}

// --- Estado Inicial ---
const initialState: AdvancedPHState = {
    currentCalculation: null,
    calculationResult: null,
    calculationHistory: [],
    historyCount: 0,
    historyNext: null,
    historyPrevious: null,
    isCalculating: false,
    isLoadingHistory: false,
    isLoadingStats: false,
    isLoadingPresets: false,
    isLoadingBuffers: false,
    isExporting: false,
    selectedPreset: null,
    presets: [],
    presetCategories: [],
    bufferSystems: [],
    bufferSuggestions: [],
    userStats: null,
    exportProgress: 0,
    errors: {},
    warnings: [],
};

// --- Thunks Asíncronos (ACTUALIZADO) ---

export const calculateAdvancedPH = createAsyncThunk<PHCalculationResult, CalculationInput, { rejectValue: any }>(
    'advancedPH/calculate',
    async (calculationInput, { rejectWithValue }) => {
        try {
            // Llamamos directamente al endpoint a través del servicio api.ts
            // Este servicio ya se encarga de la autenticación y el refresco del token.
            const response = await api.post('calculators/advanced-ph-calculator/', calculationInput);
            return response;
        } catch (error: any) {
            // El servicio api.ts ya formatea el error, por lo que podemos pasarlo directamente.
            return rejectWithValue(error.message || 'Ocurrió un error en el cálculo.');
        }
    }
);

// Thunk para obtener el historial de cálculos
export const fetchPHHistory = createAsyncThunk<
    { results: PHCalculationHistory[]; count: number; next: string | null; previous: string | null },
    HistoryFilters | undefined,
    { rejectValue: any }
>(
    'advancedPH/fetchHistory',
    async (filters, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.getPHHistory(filters);
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al cargar el historial');
        }
    }
);

// Thunk para obtener estadísticas
export const fetchPHStats = createAsyncThunk<
    any, // Usamos any temporalmente para flexibilidad con el formato de respuesta
    void,
    { rejectValue: any }
>(
    'advancedPH/fetchStats',
    async (_, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.getPHStats();
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al cargar las estadísticas');
        }
    }
);

// Thunk para exportar cálculos
export const exportPHCalculations = createAsyncThunk<
    any,
    ExportRequest,
    { rejectValue: any }
>(
    'advancedPH/export',
    async (request, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.exportCalculations(request);
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al exportar los cálculos');
        }
    }
);

// Thunk para eliminar un cálculo
export const deleteCalculation = createAsyncThunk<
    string,
    string,
    { rejectValue: any }
>(
    'advancedPH/deleteCalculation',
    async (id, { rejectWithValue }) => {
        try {
            await phCalculatorService.deleteCalculation(id);
            return id;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al eliminar el cálculo');
        }
    }
);

// Thunk para obtener presets
export const fetchPresets = createAsyncThunk<
    any[],
    { category?: string; calculation_type?: string; search?: string } | undefined,
    { rejectValue: any }
>(
    'advancedPH/fetchPresets',
    async (filters, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.getChemicalPresets(filters);
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al cargar presets');
        }
    }
);

// Thunk para obtener categorías de presets
export const fetchPresetCategories = createAsyncThunk<
    any[],
    void,
    { rejectValue: any }
>(
    'advancedPH/fetchPresetCategories',
    async (_, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.getPresetCategories();
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al cargar categorías');
        }
    }
);

// Thunk para usar un preset
export const usePreset = createAsyncThunk<
    { success: boolean; message: string; calculation_input: any },
    string,
    { rejectValue: any }
>(
    'advancedPH/usePreset',
    async (presetId, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.usePreset(presetId);
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al usar el preset');
        }
    }
);

// Thunk para obtener sistemas buffer
export const fetchBufferSystems = createAsyncThunk<
    any[],
    { min_ph?: number; max_ph?: number; search?: string } | undefined,
    { rejectValue: any }
>(
    'advancedPH/fetchBufferSystems',
    async (filters, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.getBufferSystems(filters);
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al cargar sistemas buffer');
        }
    }
);

// Thunk para obtener sugerencias de buffer
export const fetchBufferSuggestions = createAsyncThunk<
    { target_ph: number; suggestions: any[]; total_found: number },
    { targetPH: number; limit?: number },
    { rejectValue: any }
>(
    'advancedPH/fetchBufferSuggestions',
    async ({ targetPH, limit = 5 }, { rejectWithValue }) => {
        try {
            const response = await phCalculatorService.getBufferSuggestions(targetPH, limit);
            return response;
        } catch (error: any) {
            return rejectWithValue(error.message || 'Error al obtener sugerencias de buffer');
        }
    }
);


// --- Slice Definition (sin cambios) ---
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
            const newCalculation = { ...state.currentCalculation, ...action.payload.values };
            if(newCalculation.calculation_type) {
                state.currentCalculation = newCalculation as CalculationInput;
            }
        },
        clearErrors: (state) => {
            state.errors = {};
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(calculateAdvancedPH.pending, (state) => {
                state.isCalculating = true;
                state.calculationResult = null;
                state.errors = {};
                state.warnings = [];
            })
            .addCase(calculateAdvancedPH.fulfilled, (state, action) => {
                state.isCalculating = false;
                state.calculationResult = action.payload;
                state.warnings = action.payload.warnings || [];
            })
            .addCase(calculateAdvancedPH.rejected, (state, action) => {
                state.isCalculating = false;
                state.errors.calculation = action.payload;
            })
            // Historial
            .addCase(fetchPHHistory.pending, (state) => {
                state.isLoadingHistory = true;
                state.errors.history = null;
            })
            .addCase(fetchPHHistory.fulfilled, (state, action) => {
                state.isLoadingHistory = false;
                state.calculationHistory = action.payload.results;
                state.historyCount = action.payload.count;
                state.historyNext = action.payload.next;
                state.historyPrevious = action.payload.previous;
            })
            .addCase(fetchPHHistory.rejected, (state, action) => {
                state.isLoadingHistory = false;
                state.errors.history = action.payload;
            })
            // Estadísticas
            .addCase(fetchPHStats.pending, (state) => {
                state.isLoadingStats = true;
                state.errors.stats = null;
            })
            .addCase(fetchPHStats.fulfilled, (state, action) => {
                state.isLoadingStats = false;
                state.userStats = action.payload;
            })
            .addCase(fetchPHStats.rejected, (state, action) => {
                state.isLoadingStats = false;
                state.errors.stats = action.payload;
            })
            // Exportación
            .addCase(exportPHCalculations.pending, (state) => {
                state.isExporting = true;
                state.errors.export = null;
            })
            .addCase(exportPHCalculations.fulfilled, (state) => {
                state.isExporting = false;
            })
            .addCase(exportPHCalculations.rejected, (state, action) => {
                state.isExporting = false;
                state.errors.export = action.payload;
            })
            // Eliminación
            .addCase(deleteCalculation.fulfilled, (state, action) => {
                state.calculationHistory = state.calculationHistory.filter(
                    calc => calc.key !== action.payload
                );
                state.historyCount = Math.max(0, state.historyCount - 1);
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