import axios from 'axios';

// --- Tipos de Datos (Importar desde un archivo de tipos compartidos) ---
// Estos tipos deben coincidir con los definidos en los componentes y el slice de Redux.
interface CalculationInput { [key: string]: any; }
interface PHResult { [key: string]: any; }
interface HistoryFilters { [key: string]: any; }
interface PHHistory { [key: string]: any; }
interface PHStats { [key: string]: any; }
interface ExportRequest { [key: string]: any; }
interface ExportResult { [key: string]: any; }
interface BufferSuggestion { [key: string]: any; }
interface ValidationResult { isValid: boolean; message?: string; }


// --- Configuración de Axios ---
const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
    timeout: 30000, // Timeout de 30 segundos para cálculos complejos
    headers: {
        'Content-Type': 'application/json',
    },
});

// --- Interceptores para Estados de Carga (Conceptual) ---
// En una app real, esto despacharía acciones a Redux para mostrar un spinner global.
apiClient.interceptors.request.use(config => {
    // store.dispatch(setGlobalLoading(true));
    console.log('Starting API request...');
    return config;
}, error => {
    // store.dispatch(setGlobalLoading(false));
    return Promise.reject(error);
});

apiClient.interceptors.response.use(response => {
    // store.dispatch(setGlobalLoading(false));
    console.log('API request finished.');
    return response;
}, error => {
    // store.dispatch(setGlobalLoading(false));
    // Manejo de errores específico
    if (error.response) {
        // Errores específicos de química enviados por el backend
        if (error.response.data.error_type === 'ChemistryError') {
            console.error('Chemistry calculation error:', error.response.data.message);
        }
    } else if (error.request) {
        // Fallo de red
        console.error('Network error:', error.message);
        // Aquí se podría implementar la lógica de reintento
    }
    return Promise.reject(error);
});


// --- Cache Local Simple (En memoria) ---
const localCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutos

const getFromCache = (key: string) => {
    const cached = localCache.get(key);
    if (cached && (Date.now() - cached.timestamp < CACHE_TTL)) {
        return cached.data;
    }
    return null;
};

const setInCache = (key: string, data: any) => {
    localCache.set(key, { data, timestamp: Date.now() });
};


// --- Funciones del Servicio ---

const advancedPHService = {
    /**
     * Envía los datos de cálculo al endpoint principal.
     */
    async calculateAdvancedPH(data: CalculationInput): Promise<PHResult> {
        const response = await apiClient.post('/calculators/advanced-ph-calculator/', data);
        return response.data;
    },

    /**
     * Obtiene el historial de cálculos con filtros y paginación.
     */
    async getPHHistory(filters: HistoryFilters): Promise<PHHistory[]> {
        const response = await apiClient.get('/calculators/ph-history/', { params: filters });
        return response.data;
    },

    /**
     * Obtiene las estadísticas de uso para un rango de tiempo.
     */
    async getPHStats(timeRange: string): Promise<PHStats> {
        const response = await apiClient.get(`/calculators/ph-stats/`, { params: { range: timeRange } });
        return response.data;
    },

    /**
     * Solicita la exportación de cálculos en un formato específico.
     */
    async exportPHCalculations(exportData: ExportRequest): Promise<ExportResult> {
        const response = await apiClient.post('/calculators/export-history/', exportData);
        return response.data; // Debería contener una URL de descarga o un blob
    },

    /**
     * Obtiene recomendaciones de buffers para un pH objetivo. Usa cache.
     */
    async getBufferRecommendations(pH: number): Promise<BufferSuggestion[]> {
        const cacheKey = `buffer_recommendations_${pH}`;
        const cachedData = getFromCache(cacheKey);
        if (cachedData) {
            return Promise.resolve(cachedData);
        }
        
        const response = await apiClient.get('/calculators/buffer-recommendations/', { params: { target_ph: pH } });
        setInCache(cacheKey, response.data);
        return response.data;
    },

    /**
     * Valida una fórmula química contra el backend.
     */
    async validateChemicalFormula(formula: string): Promise<ValidationResult> {
        try {
            const response = await apiClient.post('/validators/validate-formula/', { formula });
            return response.data;
        } catch (error: any) {
            return { isValid: false, message: error.response?.data?.detail || 'Error de validación' };
        }
    },
};

export default advancedPHService;