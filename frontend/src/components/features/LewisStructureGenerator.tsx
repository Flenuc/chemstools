import React, { useState, useEffect, useRef } from 'react';

// Type definitions for the backend API response
interface AtomData {
  index: number;
  symbol: string;
  formal_charge: number;
  lone_pairs: number;
  hybridization: string;
  position: [number, number];
}

interface BondData {
  begin_atom: number;
  end_atom: number;
  order: number;
  is_aromatic: boolean;
}

interface LewisData {
  formula: string;
  total_valence_electrons: number;
  atom_counts: Record<string, number>;
  atoms: AtomData[];
  bonds: BondData[];
  molecular_weight: number;
}

interface StructureResponse {
  id: number;
  formula: string;
  mol_data: string;
  lewis_data: LewisData;
  created_at: string;
}

interface ApiError {
  error: string;
  details?: any;
}

const LewisStructureGenerator: React.FC = () => {
  // State management
  const [formula, setFormula] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [structureData, setStructureData] = useState<StructureResponse | null>(null);
  const [validationError, setValidationError] = useState<string>('');
  const [kekuleLoaded, setKekuleLoaded] = useState<boolean>(false);
  
  // Refs for canvas and molecular viewer
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const viewerContainerRef = useRef<HTMLDivElement>(null);

  // Supported molecules for quick selection
  const supportedMolecules = [
    'H2O', 'CH4', 'NH3', 'CO2', 'C2H6', 'C2H4', 'C2H2', 
    'HCl', 'HF', 'H2S', 'PH3', 'CH3OH', 'CH2O', 'C2H5OH',
    'SO2', 'PCl3', 'BF3', 'SF6', 'ClF3', 'XeF4'
  ];

  // Load Kekule.js dynamically
  useEffect(() => {
    const loadKekule = async () => {
      try {
        // Load Kekule.js from CDN
        if (!(window as any).Kekule) {
          const script = document.createElement('script');
          script.src = 'https://unpkg.com/kekule@0.7.4/dist/kekule.min.js';
          script.onload = () => {
            setKekuleLoaded(true);
            console.log('Kekule.js loaded successfully');
          };
          script.onerror = () => {
            console.warn('Failed to load Kekule.js, falling back to canvas renderer');
            setKekuleLoaded(false);
          };
          document.head.appendChild(script);
        } else {
          setKekuleLoaded(true);
        }
      } catch (error) {
        console.warn('Error loading Kekule.js:', error);
        setKekuleLoaded(false);
      }
    };
    
    loadKekule();
  }, []);

  // Formula validation
  const validateFormula = (input: string): boolean => {
    const formulaRegex = /^[A-Z][a-z]?(\d*[A-Z][a-z]?\d*)*$/;
    return formulaRegex.test(input);
  };

  // Handle input change with validation
  const handleFormulaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.trim();
    setFormula(value);
    
    if (value && !validateFormula(value)) {
      setValidationError('Formato inválido de fórmula molecular. Usa formato como H2O, CH4, etc.');
    } else {
      setValidationError('');
    }
    
    // Clear previous results when input changes
    if (value !== structureData?.formula) {
      setStructureData(null);
      setError(null);
    }
  };

  // Mock API call for demo purposes
  const generateStructure = async (formulaInput: string): Promise<StructureResponse> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock data for common molecules
    const mockData: Record<string, StructureResponse> = {
      'CO2': {
        id: 1,
        formula: 'CO2',
        mol_data: '',
        lewis_data: {
          formula: 'CO2',
          total_valence_electrons: 16,
          atom_counts: { C: 1, O: 2 },
          molecular_weight: 44.01,
          atoms: [
            { index: 0, symbol: 'O', formal_charge: 0, lone_pairs: 2, hybridization: 'sp', position: [-2, 0] },
            { index: 1, symbol: 'C', formal_charge: 0, lone_pairs: 0, hybridization: 'sp', position: [0, 0] },
            { index: 2, symbol: 'O', formal_charge: 0, lone_pairs: 2, hybridization: 'sp', position: [2, 0] }
          ],
          bonds: [
            { begin_atom: 0, end_atom: 1, order: 2, is_aromatic: false },
            { begin_atom: 1, end_atom: 2, order: 2, is_aromatic: false }
          ]
        },
        created_at: new Date().toISOString()
      },
      'H2O': {
        id: 2,
        formula: 'H2O',
        mol_data: '',
        lewis_data: {
          formula: 'H2O',
          total_valence_electrons: 8,
          atom_counts: { H: 2, O: 1 },
          molecular_weight: 18.015,
          atoms: [
            { index: 0, symbol: 'O', formal_charge: 0, lone_pairs: 2, hybridization: 'sp3', position: [0, 0] },
            { index: 1, symbol: 'H', formal_charge: 0, lone_pairs: 0, hybridization: 's', position: [-1.2, 0.8] },
            { index: 2, symbol: 'H', formal_charge: 0, lone_pairs: 0, hybridization: 's', position: [1.2, 0.8] }
          ],
          bonds: [
            { begin_atom: 0, end_atom: 1, order: 1, is_aromatic: false },
            { begin_atom: 0, end_atom: 2, order: 1, is_aromatic: false }
          ]
        },
        created_at: new Date().toISOString()
      },
      'NH3': {
        id: 3,
        formula: 'NH3',
        mol_data: '',
        lewis_data: {
          formula: 'NH3',
          total_valence_electrons: 8,
          atom_counts: { N: 1, H: 3 },
          molecular_weight: 17.031,
          atoms: [
            { index: 0, symbol: 'N', formal_charge: 0, lone_pairs: 1, hybridization: 'sp3', position: [0, 0] },
            { index: 1, symbol: 'H', formal_charge: 0, lone_pairs: 0, hybridization: 's', position: [-1, -1] },
            { index: 2, symbol: 'H', formal_charge: 0, lone_pairs: 0, hybridization: 's', position: [1, -1] },
            { index: 3, symbol: 'H', formal_charge: 0, lone_pairs: 0, hybridization: 's', position: [0, 1.2] }
          ],
          bonds: [
            { begin_atom: 0, end_atom: 1, order: 1, is_aromatic: false },
            { begin_atom: 0, end_atom: 2, order: 1, is_aromatic: false },
            { begin_atom: 0, end_atom: 3, order: 1, is_aromatic: false }
          ]
        },
        created_at: new Date().toISOString()
      }
    };

    if (mockData[formulaInput]) {
      return mockData[formulaInput];
    } else {
      throw new Error(`Estructura no disponible para ${formulaInput}. Usa CO2, H2O o NH3 para la demostración.`);
    }
  };

  // Handle structure generation
  const handleSubmit = async (e: React.MouseEvent | React.KeyboardEvent) => {
    e.preventDefault();
    
    if (!formula || !validateFormula(formula)) {
      setValidationError('Por favor, ingresa una fórmula molecular válida');
      return;
    }

    setLoading(true);
    setError(null);
    setStructureData(null);

    try {
      const result = await generateStructure(formula);
      setStructureData(result);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al generar la estructura';
      setError(errorMessage);
      setStructureData(null);
    } finally {
      setLoading(false);
    }
  };

  // Quick select handler
  const handleQuickSelect = (selectedFormula: string) => {
    setFormula(selectedFormula);
    setValidationError('');
    setError(null);
  };

  // Enhanced molecular structure renderer with better visuals
  const renderMolecularStructure = () => {
    if (!structureData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas with white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    const { atoms, bonds } = structureData.lewis_data;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const scale = 60;

    // Enhanced color scheme
    const atomColors: Record<string, string> = {
      'C': '#404040',
      'O': '#FF0D0D',
      'N': '#3050F8',
      'H': '#FFFFFF',
      'S': '#FFFF30',
      'P': '#FF8000',
      'F': '#90E050',
      'Cl': '#1FF01F',
      'Br': '#A62929',
      'I': '#940094'
    };

    // Draw bonds with improved styling
    bonds.forEach(bond => {
      const beginAtom = atoms[bond.begin_atom];
      const endAtom = atoms[bond.end_atom];
      
      const x1 = centerX + beginAtom.position[0] * scale;
      const y1 = centerY - beginAtom.position[1] * scale; // Flip Y axis
      const x2 = centerX + endAtom.position[0] * scale;
      const y2 = centerY - endAtom.position[1] * scale;

      // Calculate bond direction
      const dx = x2 - x1;
      const dy = y2 - y1;
      const length = Math.sqrt(dx * dx + dy * dy);
      const unitX = dx / length;
      const unitY = dy / length;
      const perpX = -unitY;
      const perpY = unitX;

      ctx.strokeStyle = '#2c3e50';
      ctx.lineWidth = bond.is_aromatic ? 3 : 2;
      ctx.lineCap = 'round';

      if (bond.order === 1) {
        // Single bond
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      } else if (bond.order === 2) {
        // Double bond
        const offset = 6;
        ctx.beginPath();
        ctx.moveTo(x1 + perpX * offset, y1 + perpY * offset);
        ctx.lineTo(x2 + perpX * offset, y2 + perpY * offset);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(x1 - perpX * offset, y1 - perpY * offset);
        ctx.lineTo(x2 - perpX * offset, y2 - perpY * offset);
        ctx.stroke();
      } else if (bond.order === 3) {
        // Triple bond
        const offset = 8;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(x1 + perpX * offset, y1 + perpY * offset);
        ctx.lineTo(x2 + perpX * offset, y2 + perpY * offset);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(x1 - perpX * offset, y1 - perpY * offset);
        ctx.lineTo(x2 - perpX * offset, y2 - perpY * offset);
        ctx.stroke();
      }
    });

    // Draw atoms with enhanced styling
    atoms.forEach(atom => {
      const x = centerX + atom.position[0] * scale;
      const y = centerY - atom.position[1] * scale;

      const atomColor = atomColors[atom.symbol] || '#808080';
      const radius = atom.symbol === 'H' ? 12 : 18;

      // Draw atom shadow
      ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
      ctx.beginPath();
      ctx.arc(x + 2, y + 2, radius, 0, 2 * Math.PI);
      ctx.fill();

      // Draw atom circle
      ctx.fillStyle = atomColor;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();

      // Add border for better definition
      ctx.strokeStyle = '#2c3e50';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Draw atom label
      ctx.fillStyle = atom.symbol === 'H' ? '#000000' : '#FFFFFF';
      ctx.font = 'bold 14px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(atom.symbol, x, y);

      // Draw formal charge if non-zero
      if (atom.formal_charge !== 0) {
        const chargeText = atom.formal_charge > 0 ? `+${atom.formal_charge}` : `${atom.formal_charge}`;
        ctx.fillStyle = '#e74c3c';
        ctx.font = 'bold 12px Arial';
        ctx.fillText(chargeText, x + 15, y - 15);
      }

      // Draw lone pairs with improved visualization
      if (atom.lone_pairs > 0) {
        ctx.fillStyle = '#e74c3c';
        const pairRadius = 4;
        const lpDistance = 28;
        
        for (let i = 0; i < atom.lone_pairs; i++) {
          const angle = (i * 2 * Math.PI) / Math.max(atom.lone_pairs, 2) - Math.PI / 2;
          const lpX = x + Math.cos(angle) * lpDistance;
          const lpY = y + Math.sin(angle) * lpDistance;
          
          // Draw two dots for each lone pair
          ctx.beginPath();
          ctx.arc(lpX - 3, lpY, pairRadius, 0, 2 * Math.PI);
          ctx.fill();
          
          ctx.beginPath();
          ctx.arc(lpX + 3, lpY, pairRadius, 0, 2 * Math.PI);
          ctx.fill();
        }
      }
    });
  };

  // Effect to render structure when data changes
  useEffect(() => {
    if (structureData) {
      // Try to use Kekule.js if available, otherwise fallback to canvas
      if (kekuleLoaded && (window as any).Kekule && structureData.mol_data) {
        try {
          // Use Kekule.js for rendering (placeholder - would need mol_data)
          renderMolecularStructure();
        } catch (error) {
          console.warn('Kekule.js rendering failed, using canvas fallback');
          renderMolecularStructure();
        }
      } else {
        renderMolecularStructure();
      }
    }
  }, [structureData, kekuleLoaded]);

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 min-h-screen">
      <div className="bg-white rounded-2xl shadow-2xl p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center items-center gap-4 mb-6">
            <div className="text-5xl animate-pulse">⚛️</div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Generador de Estructuras de Lewis
            </h1>
            <div className="text-5xl animate-bounce">🧪</div>
          </div>
          <p className="text-gray-600 text-lg">Genera y visualiza estructuras de Lewis precisas a partir de fórmulas moleculares</p>
          {kekuleLoaded ? (
            <div className="mt-2 text-green-600 text-sm flex items-center justify-center gap-2">
              <span>✅</span> Kekule.js cargado - Renderizado avanzado disponible
            </div>
          ) : (
            <div className="mt-2 text-blue-600 text-sm flex items-center justify-center gap-2">
              <span>⚡</span> Usando renderizado canvas mejorado
            </div>
          )}
        </div>

        {/* Input Section */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row gap-4 items-end">
            <div className="flex-1">
              <label htmlFor="formula" className="block text-sm font-semibold text-gray-700 mb-3">
                Fórmula Molecular
              </label>
              <input
                id="formula"
                type="text"
                value={formula}
                onChange={handleFormulaChange}
                placeholder="Ingresa la fórmula molecular (ej: H2O, CH4, NH3, CO2)"
                className={`w-full px-6 py-4 border-2 rounded-xl text-lg focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all ${
                  validationError ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                }`}
                disabled={loading}
                onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
              />
              {validationError && (
                <p className="mt-2 text-sm text-red-600 flex items-center gap-2 bg-red-50 p-2 rounded-lg">
                  <span className="text-red-500">⚠️</span>
                  {validationError}
                </p>
              )}
            </div>
            <button
              onClick={handleSubmit}
              disabled={loading || !!validationError || !formula}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 focus:ring-4 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 transition-all transform hover:scale-105 disabled:hover:scale-100"
            >
              {loading ? (
                <>
                  <span className="animate-spin text-xl">⏳</span>
                  Generando...
                </>
              ) : (
                <>
                  <span className="text-xl">🔍</span>
                  Generar Estructura
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Select */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Selección Rápida:</h3>
          <div className="flex flex-wrap gap-3">
            {supportedMolecules.map((mol) => (
              <button
                key={mol}
                onClick={() => handleQuickSelect(mol)}
                className="px-4 py-2 text-sm font-medium bg-gradient-to-r from-gray-100 to-gray-200 hover:from-blue-100 hover:to-blue-200 text-gray-700 hover:text-blue-700 rounded-lg transition-all transform hover:scale-105 border border-gray-300 hover:border-blue-300"
                disabled={loading}
              >
                {mol}
              </button>
            ))}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-6 bg-red-50 border-l-4 border-red-400 rounded-lg">
            <div className="flex items-center gap-3">
              <span className="text-red-600 text-2xl">❌</span>
              <div>
                <span className="text-red-800 font-semibold text-lg">Error</span>
                <p className="text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {structureData && (
          <div className="space-y-8">
            {/* Success Message */}
            <div className="p-6 bg-green-50 border-l-4 border-green-400 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-green-600 text-2xl">✅</span>
                <div>
                  <span className="text-green-800 font-semibold text-lg">¡Estructura Generada Exitosamente!</span>
                  <p className="text-green-700 text-sm">La estructura de Lewis ha sido calculada y renderizada</p>
                </div>
              </div>
            </div>

            {/* Molecular Structure Visualization */}
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-8 shadow-inner">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                Estructura de Lewis: <span className="text-blue-600">{structureData.formula}</span>
              </h3>
              <div className="bg-white rounded-xl border-4 border-dashed border-gray-300 p-6 shadow-lg">
                <canvas
                  ref={canvasRef}
                  width={600}
                  height={450}
                  className="mx-auto block rounded-lg"
                  style={{ maxWidth: '100%', height: 'auto' }}
                />
              </div>
            </div>

            {/* Molecular Properties */}
            <div className="grid lg:grid-cols-2 gap-8">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 shadow-lg">
                <h4 className="font-bold text-blue-900 text-xl mb-4 flex items-center gap-2">
                  <span>📊</span> Propiedades Moleculares
                </h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg">
                    <span className="text-gray-700 font-medium">Fórmula:</span>
                    <span className="font-mono text-lg font-bold text-blue-600">{structureData.lewis_data.formula}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg">
                    <span className="text-gray-700 font-medium">Electrones de Valencia:</span>
                    <span className="font-mono text-lg font-bold text-purple-600">{structureData.lewis_data.total_valence_electrons}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg">
                    <span className="text-gray-700 font-medium">Peso Molecular:</span>
                    <span className="font-mono text-lg font-bold text-green-600">{structureData.lewis_data.molecular_weight.toFixed(3)} g/mol</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 shadow-lg">
                <h4 className="font-bold text-purple-900 text-xl mb-4 flex items-center gap-2">
                  <span>🧮</span> Composición Atómica
                </h4>
                <div className="space-y-3">
                  {Object.entries(structureData.lewis_data.atom_counts).map(([element, count]) => (
                    <div key={element} className="flex justify-between items-center p-3 bg-white rounded-lg">
                      <span className="text-gray-700 font-medium">{element}:</span>
                      <span className="font-mono text-lg font-bold text-purple-600">{count} átomo{count > 1 ? 's' : ''}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Atom Details */}
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-6 shadow-lg">
              <h4 className="font-bold text-indigo-900 text-xl mb-6 flex items-center gap-2">
                <span>🔬</span> Detalles Atómicos
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm bg-white rounded-lg overflow-hidden shadow">
                  <thead className="bg-indigo-600 text-white">
                    <tr>
                      <th className="text-left py-4 px-4 font-semibold">Índice</th>
                      <th className="text-left py-4 px-4 font-semibold">Elemento</th>
                      <th className="text-left py-4 px-4 font-semibold">Carga Formal</th>
                      <th className="text-left py-4 px-4 font-semibold">Pares Solitarios</th>
                      <th className="text-left py-4 px-4 font-semibold">Hibridación</th>
                    </tr>
                  </thead>
                  <tbody>
                    {structureData.lewis_data.atoms.map((atom, idx) => (
                      <tr key={atom.index} className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                        <td className="py-3 px-4 font-mono font-bold">{atom.index}</td>
                        <td className="py-3 px-4 font-semibold text-lg">{atom.symbol}</td>
                        <td className="py-3 px-4 font-mono">{atom.formal_charge}</td>
                        <td className="py-3 px-4 font-mono">{atom.lone_pairs}</td>
                        <td className="py-3 px-4 font-mono">{atom.hybridization}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LewisStructureGenerator;