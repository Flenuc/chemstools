import { api } from './api';
import { 
  PHCalculationHistory, 
  PHUserStats, 
  HistoryFilters,
  ExportRequest,
  BufferSuggestion 
} from '../types/advancedPH';

/**
 * Servicio para interactuar con la API de la calculadora de pH
 */
export const phCalculatorService = {
  /**
   * Obtiene el historial de cálculos del usuario
   */
  async getPHHistory(filters?: HistoryFilters): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: PHCalculationHistory[];
  }> {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.page) params.append('page', filters.page.toString());
      if (filters.pageSize) params.append('page_size', filters.pageSize.toString());
      if (filters.calculationType) params.append('calculation_type', filters.calculationType);
      if (filters.searchQuery) params.append('search', filters.searchQuery);
      if (filters.dateRange) {
        params.append('date_from', filters.dateRange[0]);
        params.append('date_to', filters.dateRange[1]);
      }
    }
    
    const queryString = params.toString();
    const endpoint = `calculators/ph-calculation-history/${queryString ? `?${queryString}` : ''}`;
    
    return await api.get(endpoint);
  },

  /**
   * Obtiene un cálculo específico por ID
   */
  async getPHCalculation(id: string): Promise<PHCalculationHistory> {
    return await api.get(`calculators/ph-calculation-history/${id}/`);
  },

  /**
   * Obtiene el resumen del historial del usuario
   */
  async getPHHistorySummary(): Promise<{
    total_calculations: number;
    calculation_types: Record<string, {
      count: number;
      display_name: string;
      percentage: number;
    }>;
    recent_activity: {
      last_7_days: number;
      daily_average: number;
    };
    performance_stats: {
      average_calculation_time_ms: number;
      calculations_with_warnings: number;
      warning_rate_percentage: number;
    };
  }> {
    return await api.get('calculators/ph-calculation-history/summary/');
  },

  /**
   * Obtiene las estadísticas del usuario
   */
  async getPHStats(): Promise<{
    usage_stats: {
      total_calculations: number;
      calculation_types: Record<string, any>;
      favorite_calculation_type: string;
      calculations_with_warnings: number;
      warning_rate: number;
    };
    calculation_trends: {
      last_24_hours: number;
      last_7_days: number;
      last_30_days: number;
      daily_average_last_week: number;
      daily_average_last_month: number;
    };
    performance_metrics: {
      average_time_ms: number;
      fastest_calculation_ms: number;
      slowest_calculation_ms: number;
      speed_distribution: Record<string, any>;
    };
    chemistry_insights: Array<{
      type: string;
      message: string;
      recommendation: string;
    }>;
  }> {
    return await api.get('calculators/ph-calculation-stats/');
  },

  /**
   * Exporta cálculos en el formato especificado
   */
  async exportCalculations(request: ExportRequest): Promise<{
    success: boolean;
    data?: {
      download_url: string;
      expires_at: string;
      file_size_bytes: number;
      total_calculations: number;
      format: string;
      includes_steps: boolean;
      includes_warnings: boolean;
    };
    error?: string;
  }> {
    const body = {
      calculation_ids: request.calculationIds,
      format: request.format,
      include_steps: request.includeSteps,
      include_warnings: request.fields.includes('warnings')
    };
    
    return await api.post('calculators/export-ph-calculations/', body);
  },

  /**
   * Obtiene sugerencias de sistemas buffer para un pH objetivo
   */
  async getBufferSuggestions(targetPH: number, limit: number = 5): Promise<{
    target_ph: number;
    suggestions: any[];
    total_found: number;
  }> {
    return await api.get(`calculators/buffer-suggestions/?target_ph=${targetPH}&limit=${limit}`);
  },

  /**
   * Obtiene los presets químicos disponibles
   */
  async getChemicalPresets(filters?: {
    category?: string;
    calculation_type?: string;
    search?: string;
    difficulty?: number;
  }): Promise<any[]> {
    const params = new URLSearchParams();
    if (filters) {
      if (filters.category) params.append('category', filters.category);
      if (filters.calculation_type) params.append('calculation_type', filters.calculation_type);
      if (filters.search) params.append('search', filters.search);
      if (filters.difficulty) params.append('difficulty', filters.difficulty.toString());
    }
    const queryString = params.toString();
    return await api.get(`calculators/presets/${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Obtiene un preset específico por ID
   */
  async getPreset(id: string): Promise<any> {
    return await api.get(`calculators/presets/${id}/`);
  },

  /**
   * Marca un preset como usado
   */
  async usePreset(id: string): Promise<{
    success: boolean;
    message: string;
    calculation_input: any;
  }> {
    return await api.post(`calculators/presets/${id}/use/`, {});
  },

  /**
   * Obtiene los presets más populares
   */
  async getPopularPresets(limit: number = 10): Promise<any[]> {
    return await api.get(`calculators/presets/popular/?limit=${limit}`);
  },

  /**
   * Obtiene las categorías de presets disponibles
   */
  async getPresetCategories(): Promise<Array<{
    code: string;
    name: string;
    count: number;
  }>> {
    return await api.get('calculators/presets/categories/');
  },

  /**
   * Obtiene los sistemas buffer disponibles
   */
  async getBufferSystems(filters?: {
    min_ph?: number;
    max_ph?: number;
    search?: string;
  }): Promise<any[]> {
    const params = new URLSearchParams();
    if (filters) {
      if (filters.min_ph) params.append('min_ph', filters.min_ph.toString());
      if (filters.max_ph) params.append('max_ph', filters.max_ph.toString());
      if (filters.search) params.append('search', filters.search);
    }
    const queryString = params.toString();
    return await api.get(`calculators/buffer-systems/${queryString ? `?${queryString}` : ''}`);
  },

  /**
   * Obtiene un sistema buffer específico
   */
  async getBufferSystem(id: string): Promise<any> {
    return await api.get(`calculators/buffer-systems/${id}/`);
  },

  /**
   * Marca un sistema buffer como usado
   */
  async useBufferSystem(id: string): Promise<{
    success: boolean;
    message: string;
  }> {
    return await api.post(`calculators/buffer-systems/${id}/use/`, {});
  },

  /**
   * Búsqueda unificada de presets y buffers
   */
  async searchPresetsAndBuffers(query: string): Promise<{
    chemical_presets: any[];
    buffer_systems: any[];
    query: string;
    total_results: number;
  }> {
    return await api.get(`calculators/preset-search/?q=${encodeURIComponent(query)}`);
  },

  /**
   * Elimina un cálculo del historial
   */
  async deleteCalculation(id: string): Promise<void> {
    return await api.delete(`calculators/ph-calculation-history/${id}/`);
  },

  /**
   * Duplica un cálculo existente
   */
  async duplicateCalculation(id: string): Promise<PHCalculationHistory> {
    return await api.post(`calculators/ph-calculation-history/${id}/duplicate/`, {});
  }
};

export default phCalculatorService;
