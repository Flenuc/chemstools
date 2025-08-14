import React, { useState, useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { addNotification } from '@/store/notificationsSlice';

// Helper function to get the correct API URL
const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    const port = window.location.port;
    // Si estamos en el puerto 80 (o sin puerto) o cualquier otro puerto que no sea 3000
    // asumimos que estamos detrás de nginx y usamos rutas relativas
    if (!port || port === '80' || port !== '3000') {
      return '/api';
    }
    // Si estamos en el puerto 3000 (desarrollo local sin nginx)
    return 'http://localhost:8000/api';
  }
  return 'http://localhost:8000/api';
};

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
  // PubChem fields
  query?: string;
  iupac_name?: string;
  pubchem_cid?: number;
  common_names?: string[];
  molecular_weight?: number;
  source?: string;
}

interface ApiError {
  error: string;
  details?: any;
}

const LewisStructureGenerator: React.FC = () => {
  const dispatch = useDispatch();
  
  // State management
  const [query, setQuery] = useState<string>('');
  const [queryType, setQueryType] = useState<string>('auto');
  const [loading, setLoading] = useState<boolean>(false);
  const [searchLoading, setSearchLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [structureData, setStructureData] = useState<StructureResponse | null>(null);
  const [searchResult, setSearchResult] = useState<any | null>(null);
  const [validationError, setValidationError] = useState<string>('');
  const [kekuleLoaded, setKekuleLoaded] = useState<boolean>(false);
  const [recentStructures, setRecentStructures] = useState<StructureResponse[]>([]);
  const [cachedCompounds, setCachedCompounds] = useState<any[]>([]);
  const [showSearchHelp, setShowSearchHelp] = useState<boolean>(false);
  
  // Refs for canvas and molecular viewer
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const viewerContainerRef = useRef<HTMLDivElement>(null);

  // Query type options
  const queryTypes = [
    { value: 'auto', label: 'Detección Automática', icon: '🔍' },
    { value: 'name', label: 'Nombre (Español/Inglés)', icon: '📝' },
    { value: 'formula', label: 'Fórmula Molecular', icon: '⚛️' },
    { value: 'smiles', label: 'SMILES', icon: '🧬' },
    { value: 'inchi', label: 'InChI', icon: '🔐' }
  ];

  // Example queries for quick selection - now supporting multiple types
  const exampleQueries = {
    'Nombres Comunes': [
      { query: 'agua', type: 'name' },
      { query: 'water', type: 'name' },
      { query: 'sal', type: 'name' },
      { query: 'azúcar', type: 'name' },
      { query: 'vinagre', type: 'name' },
      { query: 'alcohol', type: 'name' },
      { query: 'acetona', type: 'name' },
      { query: 'benceno', type: 'name' }
    ],
    'Fórmulas Moleculares': [
      { query: 'H2O', type: 'formula' },
      { query: 'CO2', type: 'formula' },
      { query: 'NH3', type: 'formula' },
      { query: 'CH4', type: 'formula' },
      { query: 'C6H12O6', type: 'formula' },
      { query: 'H2SO4', type: 'formula' },
      { query: 'NaCl', type: 'formula' },
      { query: 'CaCO3', type: 'formula' }
    ],
    'SMILES': [
      { query: 'O', type: 'smiles' },
      { query: 'CCO', type: 'smiles' },
      { query: 'CC(=O)C', type: 'smiles' },
      { query: 'c1ccccc1', type: 'smiles' }
    ]
  };

  // Load Kekule.js dynamically and fetch initial data
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
    
    const loadInitialData = async () => {
      // Load recent structures
      const structures = await fetchRecentStructures();
      setRecentStructures(structures.slice(0, 5));
      
      // Load cached compounds from PubChem
      const cached = await fetchCachedCompounds();
      setCachedCompounds(cached.slice(0, 10));
    };
    
    loadKekule();
    loadInitialData();
  }, []);

  // Validate query based on type
  const validateQuery = (input: string, type: string): boolean => {
    if (!input || input.trim() === '') return false;
    
    switch (type) {
      case 'formula':
        // Basic formula validation
        const formulaRegex = /^[A-Z][a-z]?(\d*[A-Z][a-z]?\d*)*$/;
        return formulaRegex.test(input);
      case 'smiles':
        // Basic SMILES validation (very simplified)
        return input.length > 0;
      case 'inchi':
        // InChI starts with 'InChI='
        return input.startsWith('InChI=');
      case 'name':
      case 'auto':
        // Names can be anything
        return input.length > 0;
      default:
        return true;
    }
  };

  // Handle input change with validation
  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setSearchResult(null);
    
    // Clear validation error when typing
    if (validationError) {
      setValidationError('');
    }
    
    // Clear previous results when input changes significantly
    if (value !== structureData?.query && value !== structureData?.formula) {
      setStructureData(null);
      setError(null);
    }
  };

  // Handle query type change
  const handleQueryTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setQueryType(e.target.value);
    setValidationError('');
  };

  // Search compound info from PubChem
  const searchCompound = async (searchQuery: string, searchType?: string): Promise<any> => {
    try {
      const params = new URLSearchParams({ q: searchQuery });
      if (searchType && searchType !== 'auto') {
        params.append('type', searchType);
      }
      
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/structures/search/?${params}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Compound not found');
      }
      
      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error searching compound');
    }
  };

  // API call to backend for Lewis structure generation
  const generateStructure = async (queryInput: string, queryTypeInput?: string): Promise<StructureResponse> => {
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/structures/lewis-generator/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryInput,
          query_type: queryTypeInput !== 'auto' ? queryTypeInput : undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json() as ApiError;
        throw new Error(errorData.details || errorData.error || 'Error al generar la estructura');
      }

      const data = await response.json() as StructureResponse;
      
      // Transform backend response to match our interface if needed
      // The backend already returns the correct format, but we ensure compatibility
      return {
        id: data.id,
        formula: data.formula,
        mol_data: data.mol_data || '',
        lewis_data: {
          formula: data.lewis_data.formula,
          total_valence_electrons: data.lewis_data.total_valence_electrons,
          atom_counts: data.lewis_data.atom_counts,
          atoms: data.lewis_data.atoms.map((atom: any) => ({
            index: atom.index,
            symbol: atom.symbol,
            formal_charge: atom.formal_charge,
            lone_pairs: atom.lone_pairs,
            hybridization: atom.hybridization,
            position: atom.position
          })),
          bonds: data.lewis_data.bonds.map((bond: any) => ({
            begin_atom: bond.begin_atom,
            end_atom: bond.end_atom,
            order: bond.order,
            is_aromatic: bond.is_aromatic
          })),
          molecular_weight: data.lewis_data.molecular_weight
        },
        created_at: data.created_at
      };
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Error inesperado al conectar con el servidor');
    }
  };

  // Fetch recent structures from backend
  const fetchRecentStructures = async () => {
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/structures/`);
      if (response.ok) {
        const structures = await response.json();
        return structures;
      }
    } catch (error) {
      console.error('Error fetching recent structures:', error);
    }
    return [];
  };

  // Fetch cached compounds from PubChem cache
  const fetchCachedCompounds = async () => {
    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/structures/cached-compounds/?limit=10`);
      if (response.ok) {
        const compounds = await response.json();
        return compounds;
      }
    } catch (error) {
      console.error('Error fetching cached compounds:', error);
    }
    return [];
  };

  // Handle compound search
  const handleSearch = async () => {
    if (!query || query.trim() === '') {
      setValidationError('Por favor, ingresa una búsqueda');
      return;
    }

    setSearchLoading(true);
    setError(null);
    setSearchResult(null);

    try {
      const result = await searchCompound(query, queryType);
      setSearchResult(result);
      
      dispatch(addNotification({
        message: `Compuesto encontrado: ${result.molecular_formula}`,
        type: 'success'
      }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Compuesto no encontrado';
      setError(errorMessage);
      
      dispatch(addNotification({
        message: errorMessage,
        type: 'error'
      }));
    } finally {
      setSearchLoading(false);
    }
  };

  // Handle structure generation
  const handleSubmit = async (e?: React.MouseEvent | React.KeyboardEvent) => {
    if (e) e.preventDefault();
    
    if (!query || query.trim() === '') {
      const message = 'Por favor, ingresa una búsqueda válida';
      setValidationError(message);
      dispatch(addNotification({
        message,
        type: 'error'
      }));
      return;
    }

    setLoading(true);
    setError(null);
    setStructureData(null);

    try {
      dispatch(addNotification({
        message: `Generando estructura de Lewis para "${query}"...`,
        type: 'info'
      }));
      
      const result = await generateStructure(query, queryType);
      setStructureData(result);
      setError(null);
      
      // Show additional info if from PubChem
      let successMessage = `Estructura de Lewis generada exitosamente`;
      if (result.source === 'pubchem_new' || result.source === 'pubchem_formula') {
        successMessage += ` (desde PubChem: ${result.iupac_name || result.formula})`;
      }
      
      dispatch(addNotification({
        message: successMessage,
        type: 'success'
      }));
      
      // Update recent structures list
      setRecentStructures(prev => [result, ...prev.filter(s => s.formula !== result.formula)].slice(0, 5));
      
      // Update cached compounds if new from PubChem
      if (result.pubchem_cid) {
        const cached = await fetchCachedCompounds();
        setCachedCompounds(cached.slice(0, 10));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error al generar la estructura';
      setError(errorMessage);
      setStructureData(null);
      
      dispatch(addNotification({
        message: errorMessage,
        type: 'error'
      }));
    } finally {
      setLoading(false);
    }
  };

  // Quick select handler
  const handleQuickSelect = (selectedQuery: string, selectedType: string = 'auto') => {
    setQuery(selectedQuery);
    setQueryType(selectedType);
    setValidationError('');
    setError(null);
    setSearchResult(null);
    
    dispatch(addNotification({
      message: `Búsqueda "${selectedQuery}" seleccionada`,
      type: 'info'
    }));
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
    
    // Helper function to get bonds connected to an atom
    const getBondsForAtom = (atomIndex: number) => {
      return bonds.filter(bond => 
        bond.begin_atom === atomIndex || bond.end_atom === atomIndex
      );
    };
    
    // Helper function to calculate angle between two atoms
    const getAngleTo = (atom1: any, atom2: any) => {
      const dx = atom2.position[0] - atom1.position[0];
      const dy = atom2.position[1] - atom1.position[1];
      return Math.atan2(dy, dx);
    };

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
      if (atom.lone_pairs > 0 && atom.symbol !== 'H') { // Hydrogen doesn't show lone pairs
        ctx.fillStyle = '#2c3e50';
        const pairRadius = 3;
        const lpDistance = 25;
        const dotSpacing = 5;
        
        // Get bonds connected to this atom to avoid overlapping
        const atomBonds = getBondsForAtom(atom.index);
        const bondAngles: number[] = [];
        
        // Calculate angles to bonded atoms
        atomBonds.forEach(bond => {
          const otherAtomIndex = bond.begin_atom === atom.index ? bond.end_atom : bond.begin_atom;
          const otherAtom = atoms[otherAtomIndex];
          bondAngles.push(getAngleTo(atom, otherAtom));
        });
        
        // Sort bond angles
        bondAngles.sort((a, b) => a - b);
        
        // Find the best positions for lone pairs (avoiding bonds)
        const lpAngles: number[] = [];
        
        if (atom.symbol === 'O' && atomBonds.length === 2 && atom.lone_pairs === 2) {
          // Special case for water-like molecules
          // Place lone pairs perpendicular to the bonds
          const avgBondAngle = bondAngles.reduce((a, b) => a + b, 0) / bondAngles.length;
          lpAngles.push(avgBondAngle + Math.PI/2);
          lpAngles.push(avgBondAngle - Math.PI/2);
        } else if (atom.symbol === 'N' && atomBonds.length === 3 && atom.lone_pairs === 1) {
          // Special case for ammonia-like molecules
          // Place lone pair opposite to the average bond direction
          const avgBondAngle = bondAngles.reduce((a, b) => a + b, 0) / bondAngles.length;
          lpAngles.push(avgBondAngle + Math.PI);
        } else if (atomBonds.length === 1) {
          // For terminal atoms with one bond
          const bondAngle = bondAngles[0];
          if (atom.lone_pairs === 1) {
            lpAngles.push(bondAngle + Math.PI);
          } else if (atom.lone_pairs === 2) {
            lpAngles.push(bondAngle + 2*Math.PI/3);
            lpAngles.push(bondAngle - 2*Math.PI/3);
          } else if (atom.lone_pairs === 3) {
            lpAngles.push(bondAngle + Math.PI/2);
            lpAngles.push(bondAngle + Math.PI);
            lpAngles.push(bondAngle - Math.PI/2);
          }
        } else if (atomBonds.length === 0) {
          // For isolated atoms
          for (let i = 0; i < atom.lone_pairs; i++) {
            lpAngles.push((i * 2 * Math.PI) / atom.lone_pairs);
          }
        } else {
          // General case: distribute lone pairs in the largest gaps between bonds
          const gaps: {angle: number, size: number}[] = [];
          
          for (let i = 0; i < bondAngles.length; i++) {
            const nextIndex = (i + 1) % bondAngles.length;
            let gapSize = bondAngles[nextIndex] - bondAngles[i];
            if (gapSize < 0) gapSize += 2 * Math.PI;
            const gapAngle = bondAngles[i] + gapSize / 2;
            gaps.push({angle: gapAngle, size: gapSize});
          }
          
          // Sort gaps by size (largest first)
          gaps.sort((a, b) => b.size - a.size);
          
          // Place lone pairs in the largest gaps
          for (let i = 0; i < Math.min(atom.lone_pairs, gaps.length); i++) {
            lpAngles.push(gaps[i].angle);
          }
        }
        
        // Draw the lone pairs
        lpAngles.forEach(angle => {
          const lpX = x + Math.cos(angle) * lpDistance;
          const lpY = y - Math.sin(angle) * lpDistance; // Note the negative for Y
          
          // Draw two dots for each lone pair
          const perpAngle = angle + Math.PI/2;
          const dot1X = lpX + Math.cos(perpAngle) * dotSpacing/2;
          const dot1Y = lpY - Math.sin(perpAngle) * dotSpacing/2;
          const dot2X = lpX - Math.cos(perpAngle) * dotSpacing/2;
          const dot2Y = lpY + Math.sin(perpAngle) * dotSpacing/2;
          
          ctx.beginPath();
          ctx.arc(dot1X, dot1Y, pairRadius, 0, 2 * Math.PI);
          ctx.fill();
          
          ctx.beginPath();
          ctx.arc(dot2X, dot2Y, pairRadius, 0, 2 * Math.PI);
          ctx.fill();
        });
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

        {/* Enhanced Input Section with PubChem Integration */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-800">Búsqueda de Compuestos</h3>
              <button
                onClick={() => setShowSearchHelp(!showSearchHelp)}
                className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
              >
                <span>❔</span> Ayuda
              </button>
            </div>
            
            {showSearchHelp && (
              <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <h4 className="font-semibold text-blue-900 mb-2">Puedes buscar por:</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• <strong>Nombres comunes:</strong> agua, water, sal, azúcar, acetona</li>
                  <li>• <strong>Fórmulas moleculares:</strong> H2O, CO2, NaCl, C6H12O6</li>
                  <li>• <strong>SMILES:</strong> O, CCO, CC(=O)C, c1ccccc1</li>
                  <li>• <strong>Nombres IUPAC:</strong> ethanoic acid, sodium chloride</li>
                  <li>• <strong>InChI:</strong> InChI=1S/H2O/h1H2</li>
                </ul>
                <p className="mt-2 text-xs text-blue-700">
                  💡 El sistema busca automáticamente en PubChem para encontrar cualquier compuesto!
                </p>
              </div>
            )}
            
            <div className="space-y-4">
              <div>
                <label htmlFor="query" className="block text-sm font-semibold text-gray-700 mb-2">
                  Búsqueda de Compuesto
                </label>
                <div className="flex flex-col sm:flex-row gap-2">
                  <select
                    value={queryType}
                    onChange={handleQueryTypeChange}
                    className="sm:w-auto px-3 py-3 border-2 border-gray-300 rounded-lg bg-white hover:border-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                    disabled={loading}
                  >
                    {queryTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </option>
                    ))}
                  </select>
                  <input
                    id="query"
                    type="text"
                    value={query}
                    onChange={handleQueryChange}
                    placeholder={queryType === 'formula' ? "Ej: H2O, CO2, CH4" : queryType === 'name' ? "Ej: agua, water, sal" : "Ingresa tu búsqueda..."}
                    className={`flex-1 px-4 py-3 border-2 rounded-lg text-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all ${
                      validationError ? 'border-red-300 bg-red-50' : 'border-gray-300 hover:border-gray-400'
                    }`}
                    disabled={loading}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
                  />
                </div>
                {validationError && (
                  <p className="mt-2 text-sm text-red-600 flex items-center gap-2 bg-red-50 p-2 rounded-lg">
                    <span className="text-red-500">⚠️</span>
                    {validationError}
                  </p>
                )}
              </div>
              
              <div className="flex flex-col sm:flex-row gap-2 justify-center">
                <button
                  onClick={handleSearch}
                  disabled={searchLoading || !query}
                  className="px-6 py-3 bg-gradient-to-r from-green-500 to-teal-500 text-white font-semibold rounded-lg hover:from-green-600 hover:to-teal-600 focus:ring-2 focus:ring-green-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all transform hover:scale-105 disabled:hover:scale-100 whitespace-nowrap"
                >
                  {searchLoading ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      <span className="hidden sm:inline">Buscando...</span>
                      <span className="sm:hidden">Buscar</span>
                    </>
                  ) : (
                    <>
                      <span>🔍</span>
                      <span>Buscar Info</span>
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => handleSubmit()}
                  disabled={loading || !query}
                  className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all transform hover:scale-105 disabled:hover:scale-100 whitespace-nowrap"
                >
                  {loading ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      <span className="hidden sm:inline">Generando...</span>
                      <span className="sm:hidden">Generar</span>
                    </>
                  ) : (
                    <>
                      <span>⚛️</span>
                      <span>Generar Lewis</span>
                    </>
                  )}
                </button>
              </div>
            </div>
            
            {/* Search Result Preview */}
            {searchResult && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200">
                <h4 className="font-semibold text-gray-800 mb-2">Compuesto encontrado:</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                  <div>
                    <span className="text-gray-600">Fórmula:</span>
                    <span className="ml-2 font-mono font-semibold">{searchResult.molecular_formula}</span>
                  </div>
                  {searchResult.iupac_name && (
                    <div>
                      <span className="text-gray-600">IUPAC:</span>
                      <span className="ml-2">{searchResult.iupac_name}</span>
                    </div>
                  )}
                  {searchResult.molecular_weight && (
                    <div>
                      <span className="text-gray-600">Peso:</span>
                      <span className="ml-2">
                        {typeof searchResult.molecular_weight === 'number' 
                          ? `${searchResult.molecular_weight.toFixed(2)} g/mol`
                          : `${searchResult.molecular_weight} g/mol`}
                      </span>
                    </div>
                  )}
                  {searchResult.pubchem_cid && (
                    <div>
                      <span className="text-gray-600">PubChem CID:</span>
                      <span className="ml-2">{searchResult.pubchem_cid}</span>
                    </div>
                  )}
                </div>
                {searchResult.common_names && searchResult.common_names.length > 0 && (
                  <div className="mt-2">
                    <span className="text-gray-600 text-sm">Nombres comunes:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {searchResult.common_names.slice(0, 5).map((name: string, idx: number) => (
                        <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                          {name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Example Queries - Now with multiple types */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Ejemplos de Búsqueda:</h3>
          <div className="space-y-4">
            {Object.entries(exampleQueries).map(([category, queries]) => (
              <div key={category}>
                <h4 className="text-sm font-medium text-gray-600 mb-2">{category}</h4>
                <div className="flex flex-wrap gap-2">
                  {queries.map((example) => (
                    <button
                      key={example.query}
                      onClick={() => handleQuickSelect(example.query, example.type)}
                      className="px-3 py-1.5 text-sm font-medium bg-gradient-to-r from-gray-100 to-gray-200 hover:from-blue-100 hover:to-blue-200 text-gray-700 hover:text-blue-700 rounded-lg transition-all transform hover:scale-105 border border-gray-300 hover:border-blue-300"
                      disabled={loading}
                      title={`Tipo: ${example.type}`}
                    >
                      {example.query}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Popular Compounds from Cache */}
        {cachedCompounds.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">Compuestos Populares (desde PubChem):</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {cachedCompounds.map((compound) => (
                <button
                  key={`${compound.query}-${compound.query_type}`}
                  onClick={() => {
                    setQuery(compound.query);
                    setQueryType(compound.query_type);
                    handleSubmit();
                  }}
                  className="p-3 bg-gradient-to-br from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 rounded-lg border border-purple-200 hover:border-purple-300 transition-all transform hover:scale-105"
                  disabled={loading}
                >
                  <div className="text-sm font-semibold text-purple-800">{compound.molecular_formula}</div>
                  <div className="text-xs text-purple-600 mt-1">{compound.query}</div>
                  <div className="text-xs text-gray-500 mt-1">🔥 {compound.access_count} usos</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Recent Structures */}
        {recentStructures.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">Estructuras Recientes:</h3>
            <div className="flex flex-wrap gap-3">
              {recentStructures.map((structure) => (
                <button
                  key={structure.id}
                  onClick={() => {
                    setQuery(structure.query || structure.formula);
                    setStructureData(structure);
                    setValidationError('');
                    setError(null);
                    dispatch(addNotification({
                      message: `Mostrando estructura guardada de ${structure.formula}`,
                      type: 'info'
                    }));
                  }}
                  className="px-4 py-2 text-sm font-medium bg-gradient-to-r from-purple-100 to-pink-100 hover:from-purple-200 hover:to-pink-200 text-purple-700 hover:text-purple-800 rounded-lg transition-all transform hover:scale-105 border border-purple-300 hover:border-purple-400"
                  disabled={loading}
                >
                  <span className="font-mono">{structure.formula}</span>
                  <span className="text-xs ml-2 opacity-75">
                    ({new Date(structure.created_at).toLocaleDateString()})
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

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