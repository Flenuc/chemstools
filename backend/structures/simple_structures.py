"""
Definiciones hardcodeadas de estructuras simples para garantizar renderizado correcto
"""

# Estructuras simples predefinidas con coordenadas optimizadas
SIMPLE_STRUCTURES = {
    'H2O': {
        'atoms': [
            {'index': 0, 'symbol': 'O', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'H', 'position': [-1.5, -0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 2, 'symbol': 'H', 'position': [1.5, -0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 18.015
    },
    
    'NH3': {
        'atoms': [
            {'index': 0, 'symbol': 'N', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 1, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'H', 'position': [0.0, -1.5], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 2, 'symbol': 'H', 'position': [-1.3, 0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 3, 'symbol': 'H', 'position': [1.3, 0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 17.031
    },
    
    'CH4': {
        'atoms': [
            {'index': 0, 'symbol': 'C', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'H', 'position': [1.0, 1.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 2, 'symbol': 'H', 'position': [-1.0, 1.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 3, 'symbol': 'H', 'position': [1.0, -1.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 4, 'symbol': 'H', 'position': [-1.0, -1.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 4, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 16.043
    },
    
    'CO2': {
        'atoms': [
            {'index': 0, 'symbol': 'C', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'SP'},
            {'index': 1, 'symbol': 'O', 'position': [-2.0, 0.0], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP2'},
            {'index': 2, 'symbol': 'O', 'position': [2.0, 0.0], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP2'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 2, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 2, 'is_aromatic': False}
        ],
        'total_valence_electrons': 16,
        'molecular_weight': 44.009
    },
    
    'HCL': {
        'atoms': [
            {'index': 0, 'symbol': 'H', 'position': [-1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 1, 'symbol': 'Cl', 'position': [1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 36.461
    },
    
    'O2': {
        'atoms': [
            {'index': 0, 'symbol': 'O', 'position': [-1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP2'},
            {'index': 1, 'symbol': 'O', 'position': [1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP2'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 2, 'is_aromatic': False}
        ],
        'total_valence_electrons': 12,
        'molecular_weight': 31.998
    },
    
    'N2': {
        'atoms': [
            {'index': 0, 'symbol': 'N', 'position': [-1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 1, 'hybridization': 'SP'},
            {'index': 1, 'symbol': 'N', 'position': [1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 1, 'hybridization': 'SP'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 3, 'is_aromatic': False}
        ],
        'total_valence_electrons': 10,
        'molecular_weight': 28.014
    },
    
    'H2': {
        'atoms': [
            {'index': 0, 'symbol': 'H', 'position': [-0.75, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 1, 'symbol': 'H', 'position': [0.75, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 2,
        'molecular_weight': 2.016
    },
    
    'HF': {
        'atoms': [
            {'index': 0, 'symbol': 'H', 'position': [-1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 1, 'symbol': 'F', 'position': [1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 20.006
    },
    
    'SO2': {
        'atoms': [
            {'index': 0, 'symbol': 'S', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 1, 'hybridization': 'SP2'},
            {'index': 1, 'symbol': 'O', 'position': [-1.5, 0.75], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP2'},
            {'index': 2, 'symbol': 'O', 'position': [1.5, 0.75], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP2'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 2, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 2, 'is_aromatic': False}
        ],
        'total_valence_electrons': 18,
        'molecular_weight': 64.064
    },
    
    'BF3': {
        'atoms': [
            {'index': 0, 'symbol': 'B', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'SP2'},
            {'index': 1, 'symbol': 'F', 'position': [0.0, 1.5], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 2, 'symbol': 'F', 'position': [-1.3, -0.75], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 3, 'symbol': 'F', 'position': [1.3, -0.75], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 24,
        'molecular_weight': 67.807
    },
    
    'PCl3': {
        'atoms': [
            {'index': 0, 'symbol': 'P', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 1, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'Cl', 'position': [0.0, 1.8], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 2, 'symbol': 'Cl', 'position': [-1.56, -0.9], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 3, 'symbol': 'Cl', 'position': [1.56, -0.9], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 26,
        'molecular_weight': 137.333
    },
    
    'H2S': {
        'atoms': [
            {'index': 0, 'symbol': 'S', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'H', 'position': [-1.2, -0.8], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 2, 'symbol': 'H', 'position': [1.2, -0.8], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 34.081
    },
    
    'PH3': {
        'atoms': [
            {'index': 0, 'symbol': 'P', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 1, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'H', 'position': [0.0, -1.5], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 2, 'symbol': 'H', 'position': [-1.3, 0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 3, 'symbol': 'H', 'position': [1.3, 0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 33.998
    },
    
    'H3P': {
        'atoms': [
            {'index': 0, 'symbol': 'P', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 1, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'H', 'position': [0.0, -1.5], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 2, 'symbol': 'H', 'position': [-1.3, 0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 3, 'symbol': 'H', 'position': [1.3, 0.75], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 8,
        'molecular_weight': 33.998
    },
    
    'CH3OH': {
        'atoms': [
            {'index': 0, 'symbol': 'C', 'position': [-0.5, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'SP3'},
            {'index': 1, 'symbol': 'O', 'position': [1.0, 0.0], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP3'},
            {'index': 2, 'symbol': 'H', 'position': [-1.0, 1.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 3, 'symbol': 'H', 'position': [-1.0, -0.5], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 4, 'symbol': 'H', 'position': [-1.0, -0.5], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'},
            {'index': 5, 'symbol': 'H', 'position': [1.7, 0.5], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'UNSPECIFIED'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 4, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 1, 'end_atom': 5, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 14,
        'molecular_weight': 32.042
    },
    
    'NO2': {
        'atoms': [
            {'index': 0, 'symbol': 'N', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'SP2'},
            {'index': 1, 'symbol': 'O', 'position': [-1.2, 0.5], 'formal_charge': 0, 'lone_pairs': 2, 'hybridization': 'SP2'},
            {'index': 2, 'symbol': 'O', 'position': [1.2, 0.5], 'formal_charge': -1, 'lone_pairs': 3, 'hybridization': 'SP2'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 2, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 17,
        'molecular_weight': 46.006
    },
    
    'SF6': {
        'atoms': [
            {'index': 0, 'symbol': 'S', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 0, 'hybridization': 'SP3D2'},
            {'index': 1, 'symbol': 'F', 'position': [1.5, 0.0], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 2, 'symbol': 'F', 'position': [-1.5, 0.0], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 3, 'symbol': 'F', 'position': [0.0, 1.5], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 4, 'symbol': 'F', 'position': [0.0, -1.5], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 5, 'symbol': 'F', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'},
            {'index': 6, 'symbol': 'F', 'position': [0.0, 0.0], 'formal_charge': 0, 'lone_pairs': 3, 'hybridization': 'SP3'}
        ],
        'bonds': [
            {'begin_atom': 0, 'end_atom': 1, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 2, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 3, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 4, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 5, 'order': 1, 'is_aromatic': False},
            {'begin_atom': 0, 'end_atom': 6, 'order': 1, 'is_aromatic': False}
        ],
        'total_valence_electrons': 48,
        'molecular_weight': 146.055
    }
}

def get_simple_structure(formula):
    """
    Obtiene una estructura simple predefinida si existe
    
    Args:
        formula: Fórmula molecular (ej: 'H2O', 'NH3')
        
    Returns:
        Dict con la estructura o None si no está predefinida
    """
    formula_upper = formula.upper()
    
    # Manejar variantes de fórmulas comunes
    formula_variants = {
        'H3N': 'NH3',
        'NH3': 'NH3',
        'H2S': 'H2S',
        'CLH': 'HCL',
        'HCL': 'HCL',
        'CIH': 'HCL',
        'O2S': 'SO2',
        'SO2': 'SO2',
        'BF3': 'BF3',
        'F3B': 'BF3',
        'PCL3': 'PCL3',
        'CL3P': 'PCL3'
    }
    
    if formula_upper in formula_variants:
        formula_upper = formula_variants[formula_upper]
    if formula_upper in SIMPLE_STRUCTURES:
        struct = SIMPLE_STRUCTURES[formula_upper]
        # Calcular atom_counts
        atom_counts = {}
        for atom in struct['atoms']:
            symbol = atom['symbol']
            atom_counts[symbol] = atom_counts.get(symbol, 0) + 1
        
        return {
            'formula': formula_upper,
            'atoms': struct['atoms'],
            'bonds': struct['bonds'],
            'total_valence_electrons': struct['total_valence_electrons'],
            'molecular_weight': struct['molecular_weight'],
            'atom_counts': atom_counts
        }
    return None
