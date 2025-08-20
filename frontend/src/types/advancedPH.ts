export enum CalculationType {
    ConcentrationToPH = 'concentration_to_ph',
    PHToAll = 'ph_to_all',
    Buffer = 'buffer',
    ActivityCorrection = 'activity_correction',
}

export enum InputType {
    PH = 'pH',
    POH = 'pOH',
    HConcentration = '[H+]',
    OHConcentration = '[OH-]',
}

export enum ExportFormat {
    CSV = 'csv',
    PDF = 'pdf',
    JSON = 'json',
    Excel = 'excel',
}

export enum ChemicalCategory {
    StrongAcid = 'strong_acid',
    StrongBase = 'strong_base',
    Buffer = 'buffer',
    Physiological = 'physiological',
    Industrial = 'industrial',
}

// --- Interfaces Requeridas ---

export interface BufferComponent {
    acidName: string;
    acidConcentration: number;
    baseName: string;
    baseConcentration: number;
}

export interface BufferSystem {
    id: string;
    pairName: string; // e.g., "Buffer de Acetato"
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
    effectiveRange: [number, number]; // [min, max]
}

export interface BufferConstraints {
    maxTotalConcentration?: number;
    requiredIonicStrength?: number;
    temperature?: number;
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
    mode: CalculationType;
    inputType?: InputType;
    inputValue?: number;
    solute?: string;
    concentration?: number;
    temperature: number;
    ionicStrength?: number;
    buffer?: BufferComponent;
}

export interface PHCalculationResult {
    ph: number;
    poh: number;
    h_concentration: number;
    oh_concentration: number;
    is_acid: boolean;
    steps: { title: string; explanation: string; formula: string }[];
    warnings: ChemicalWarning[];
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
