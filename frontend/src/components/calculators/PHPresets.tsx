import React, { useState, useEffect, useMemo } from 'react';
import { Card, Typography, AutoComplete, Tooltip, Tabs } from 'antd';
import { motion, AnimatePresence } from 'framer-motion';
import { StarIcon as StarSolid } from '@heroicons/react/24/solid';
import { StarIcon as StarOutline, BeakerIcon, HeartIcon, BuildingOffice2Icon } from '@heroicons/react/24/outline';
// Asumiendo que CalculationInput se exporta desde AdvancedPHCalculator o un archivo de tipos compartido
 import { CalculationInput } from './AdvancedPHCalculator';

// --- Tipos de Datos ---
export interface ChemicalPreset {
    id: string;
    name: string;
    category: 'strong_acid' | 'strong_base' | 'buffer' | 'physiological' | 'industrial';
    description: string;
    values: Partial<CalculationInput>; 
}

interface PHPresetsProps {
    onPresetSelect: (preset: ChemicalPreset) => void;
    selectedPresetId?: string;
    showCategories?: boolean;
}

// --- Base de Datos de Presets ---
const allPresets: ChemicalPreset[] = [
    // Ácidos Fuertes
    { id: 'hcl_0.1', name: 'HCl 0.1M', category: 'strong_acid', description: 'Ácido clorhídrico, un ácido monoprótico fuerte común.', values: { mode: 'concentration_to_ph', solute: 'HCl', concentration: 0.1 } },
    { id: 'h2so4_0.05', name: 'H₂SO₄ 0.05M', category: 'strong_acid', description: 'Ácido sulfúrico, un ácido diprótico fuerte.', values: { mode: 'concentration_to_ph', solute: 'H2SO4', concentration: 0.05 } },
    { id: 'hno3_1.0', name: 'HNO₃ 1.0M', category: 'strong_acid', description: 'Ácido nítrico, utilizado en fertilizantes y explosivos.', values: { mode: 'concentration_to_ph', solute: 'HNO3', concentration: 1.0 } },
    // Bases Fuertes
    { id: 'naoh_0.1', name: 'NaOH 0.1M', category: 'strong_base', description: 'Hidróxido de sodio, una base fuerte muy utilizada.', values: { mode: 'concentration_to_ph', solute: 'NaOH', concentration: 0.1 } },
    { id: 'koh_0.2', name: 'KOH 0.2M', category: 'strong_base', description: 'Hidróxido de potasio, similar al NaOH.', values: { mode: 'concentration_to_ph', solute: 'KOH', concentration: 0.2 } },
    { id: 'caoh2_0.01', name: 'Ca(OH)₂ 0.01M', category: 'strong_base', description: 'Hidróxido de calcio, una base fuerte dibásica.', values: { mode: 'concentration_to_ph', solute: 'Ca(OH)2', concentration: 0.01 } },
    // Buffers
    { id: 'acetate_buffer', name: 'Buffer Acetato', category: 'buffer', description: 'CH₃COOH / CH₃COONa. pKa ≈ 4.76', values: { mode: 'buffer', buffer: { acidName: 'CH3COOH', acidConcentration: 0.1, baseName: 'CH3COONa', baseConcentration: 0.1 } } },
    { id: 'phosphate_buffer', name: 'Buffer Fosfato', category: 'buffer', description: 'H₂PO₄⁻ / HPO₄²⁻. pKa ≈ 7.21', values: { mode: 'buffer', buffer: { acidName: 'NaH2PO4', acidConcentration: 0.1, baseName: 'Na2HPO4', baseConcentration: 0.1 } } },
    // Fisiológicos
    { id: 'blood_plasma', name: 'Plasma Sanguíneo', category: 'physiological', description: 'pH fisiológico típico de la sangre humana.', values: { mode: 'ph_to_all', inputType: 'pH', inputValue: 7.4 } },
    { id: 'urine', name: 'Orina Humana', category: 'physiological', description: 'Rango de pH normal para la orina.', values: { mode: 'ph_to_all', inputType: 'pH', inputValue: 6.0 } },
    // Industriales
    { id: 'pool_water', name: 'Agua de Piscina', category: 'industrial', description: 'Rango de pH ideal para piscinas.', values: { mode: 'ph_to_all', inputType: 'pH', inputValue: 7.2 } },
];


const PresetCard: React.FC<{ preset: ChemicalPreset; isSelected: boolean; isFavorite: boolean; onSelect: () => void; onToggleFavorite: () => void; }> = 
({ preset, isSelected, isFavorite, onSelect, onToggleFavorite }) => {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            whileHover={{ scale: 1.03 }}
            className="cursor-pointer"
            onClick={onSelect}
        >
            <Card
                className={`shadow-md hover:shadow-xl transition-shadow ${isSelected ? 'border-2 border-blue-500' : ''}`}
                size="small"
            >
                <div className="flex justify-between items-start">
                    <div>
                        <Typography.Text strong>{preset.name}</Typography.Text>
                        <p className="text-xs text-gray-500">{preset.description}</p>
                    </div>
                    <Tooltip title={isFavorite ? 'Quitar de favoritos' : 'Añadir a favoritos'}>
                        <button onClick={(e) => { e.stopPropagation(); onToggleFavorite(); }} className="p-1 rounded-full hover:bg-gray-200">
                            {isFavorite ? <StarSolid className="h-5 w-5 text-yellow-500" /> : <StarOutline className="h-5 w-5 text-gray-400" />}
                        </button>
                    </Tooltip>
                </div>
            </Card>
        </motion.div>
    );
};


const PHPresets: React.FC<PHPresetsProps> = ({
    onPresetSelect,
    selectedPresetId,
    showCategories = true,
}) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [favorites, setFavorites] = useState<string[]>([]);

    useEffect(() => {
        try {
            const storedFavorites = localStorage.getItem('chemstools_ph_favorites');
            if (storedFavorites) {
                setFavorites(JSON.parse(storedFavorites));
            }
        } catch (error) {
            console.error("Failed to parse favorites from localStorage", error);
        }
    }, []);

    const toggleFavorite = (presetId: string) => {
        const newFavorites = favorites.includes(presetId)
            ? favorites.filter(id => id !== presetId)
            : [...favorites, presetId];
        setFavorites(newFavorites);
        try {
            localStorage.setItem('chemstools_ph_favorites', JSON.stringify(newFavorites));
        } catch (error) {
            console.error("Failed to save favorites to localStorage", error);
        }
    };

    const filteredPresets = useMemo(() => {
        if (!searchTerm) return allPresets;
        const lowercasedTerm = searchTerm.toLowerCase();
        // Simple fuzzy search
        return allPresets.filter(p =>
            p.name.toLowerCase().includes(lowercasedTerm) ||
            p.description.toLowerCase().includes(lowercasedTerm)
        );
    }, [searchTerm]);

    const renderPresetList = (presets: ChemicalPreset[]) => (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <AnimatePresence>
                {presets.map(preset => (
                    <PresetCard
                        key={preset.id}
                        preset={preset}
                        isSelected={selectedPresetId === preset.id}
                        isFavorite={favorites.includes(preset.id)}
                        onSelect={() => onPresetSelect(preset)}
                        onToggleFavorite={() => toggleFavorite(preset.id)}
                    />
                ))}
            </AnimatePresence>
        </div>
    );
    
    const favoritePresets = allPresets.filter(p => favorites.includes(p.id));
    const strongAcids = filteredPresets.filter(p => p.category === 'strong_acid');
    const strongBases = filteredPresets.filter(p => p.category === 'strong_base');
    const buffers = filteredPresets.filter(p => p.category === 'buffer');
    const physiological = filteredPresets.filter(p => p.category === 'physiological');
    const industrial = filteredPresets.filter(p => p.category === 'industrial');

    const tabItems = [
        { key: 'favorites', label: (<span><StarSolid className="h-4 w-4 inline-block mr-1"/>Favoritos</span>), children: renderPresetList(favoritePresets) },
        { key: 'strong_acids', label: (<span><BeakerIcon className="h-4 w-4 inline-block mr-1"/>Ácidos Fuertes</span>), children: renderPresetList(strongAcids) },
        { key: 'strong_bases', label: (<span><BeakerIcon className="h-4 w-4 inline-block mr-1"/>Bases Fuertes</span>), children: renderPresetList(strongBases) },
        { key: 'buffers', label: (<span><BeakerIcon className="h-4 w-4 inline-block mr-1"/>Buffers</span>), children: renderPresetList(buffers) },
        { key: 'physiological', label: (<span><HeartIcon className="h-4 w-4 inline-block mr-1"/>Fisiológicos</span>), children: renderPresetList(physiological) },
        { key: 'industrial', label: (<span><BuildingOffice2Icon className="h-4 w-4 inline-block mr-1"/>Industriales</span>), children: renderPresetList(industrial) },
    ];

    return (
        <Card title="Biblioteca de Presets">
            <AutoComplete
                className="w-full mb-4"
                onSearch={setSearchTerm}
                placeholder="Buscar preset por nombre o descripción..."
                allowClear
            />
            {showCategories ? (
                <Tabs defaultActiveKey="favorites" items={tabItems} />
            ) : (
                renderPresetList(filteredPresets)
            )}
        </Card>
    );
};

export default PHPresets;
