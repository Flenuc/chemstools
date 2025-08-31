export enum CalculationType {
    ConcentrationToPH = 'concentration_to_ph',
    PHToAll = 'ph_to_all',
    Buffer = 'buffer_calculation',
    ActivityCorrection = 'activity_correction',
}

export enum InputType {
    PH = 'ph',
    POH = 'poh',
    HConcentration = 'h_concentration',
    OHConcentration = 'oh_concentration'
}

export enum ExportFormat {
    CSV = 'csv',
    PDF = 'pdf',
    JSON = 'json',
    Excel = 'xlsx',
}

export enum ChemicalCategory {
    StrongAcid = 'strong_acid',
    StrongBase = 'strong_base',
    Buffer = 'buffer',
    Physiological = 'physiological',
    Industrial = 'industrial',
}

// --- Interfaces Requeridas ---

export interface BufferComponentAPI {
    compound: string;
    concentration: number;
    pka?: number;
}

export interface BufferComponent {
    acidName: string;
    acidConcentration: number;
    baseName: string;
    baseConcentration: number;
}

export interface ChemicalWarning {
    code: string;
    message: string;
    level: 'info' | 'warning' | 'critical';
}

export interface ValidationError {
    field: string;
    message: string;
}

export interface CalculationInput {
    calculation_type: CalculationType;
    input_value: number; // Siempre requerido
    input_type: InputType; // Siempre requerido
    temperature?: number;
    ionic_strength?: number;
    include_activity?: boolean;
    show_steps?: boolean;
    buffer_components?: BufferComponentAPI[];
}

export interface PHCalculationResult {
    success: boolean;
    results: {
        ph: number;
        poh: number;
        h_concentration: number;
        oh_concentration: number;
        [key: string]: any; // Para otros resultados dinámicos
    };
    calculation_steps?: string[];
    warnings?: any[];
    metadata: {
        calculation_id: string;
        calculation_time_ms: number;
    };
}

export interface PHCalculationHistory {
    key: string; // UUID
    userId: string;
    calculationType: CalculationType;
    inputSummary: string;
    result: PHCalculationResult;
    timestamp: string; // ISO 8601
    calculationTimeMs: number;
}

export interface ChemicalPreset {
    id: string;
    name: string;
    category: ChemicalCategory;
    description: string;
    values: Partial<CalculationInput>;
}

export interface ExportRequest {
    calculationIds: string[];
    format: ExportFormat;
    fields: string[];
    includeSteps: boolean;
}

export interface PHUserStats {
    totalCalculations: number;
    distribution: Record<CalculationType, number>;
    avgCalculationTime: number;
    warningRate: number;
    activity: { date: string; count: number }[];
}

export interface BufferSystem {
    id: string;
    pairName: string;
    acid: {
        formula: string;
        concentration: number;
        pKa: number;
    };
    base: {
        formula: string;
        concentration: number;
    };
    finalPH: number;
    bufferCapacity: number;
    effectiveRange: [number, number];
}

export interface BufferConstraints {
    maxTotalConcentration?: number;
    requiredIonicStrength?: number;
    temperature?: number;
}

// --- Tipos para el Servicio API (AÑADIDO) ---

export interface HistoryFilters {
    userId?: string;
    page?: number;
    pageSize?: number;
    calculationType?: CalculationType;
    dateRange?: [string, string]; // [startDate, endDate]
    searchQuery?: string;
}

export interface BufferSuggestion {
    pairName: string;
    pKa: number;
    effectiveRange: [number, number];
    suitabilityScore: number; // Un puntaje de 0 a 1
}

export interface ValidationResult {
    isValid: boolean;
    message?: string;
    normalizedFormula?: string;
}