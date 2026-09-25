import json
from typing import Dict, Any, Tuple, List
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, AllChem


class LewisStructureGenerator:
    """Generate Lewis structures using RDKit"""
    
    @staticmethod
    def parse_formula(formula: str) -> Dict[str, int]:
        """Parse molecular formula and return atom counts"""
        import re
        
        pattern = r'([A-Z][a-z]?)(\d*)'
        matches = re.findall(pattern, formula)
        
        atom_counts = {}
        for element, count in matches:
            count = int(count) if count else 1
            atom_counts[element] = atom_counts.get(element, 0) + count
            
        return atom_counts
    
    @staticmethod
    def get_valence_electrons(atom_counts: Dict[str, int]) -> int:
        """Calculate total valence electrons"""
        valence_map = {
            'H': 1, 'He': 2,
            'Li': 1, 'Be': 2, 'B': 3, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'Ne': 8,
            'Na': 1, 'Mg': 2, 'Al': 3, 'Si': 4, 'P': 5, 'S': 6, 'Cl': 7, 'Ar': 8,
            'K': 1, 'Ca': 2, 'Br': 7, 'I': 7, 'Xe': 8, 'As': 5, 'Se': 6,
            'Sc': 3, 'Ti': 4, 'V': 5, 'Cr': 6, 'Mn': 7, 'Fe': 8, 'Co': 9, 'Ni': 10,
            'Cu': 11, 'Zn': 12, 'Ga': 3, 'Ge': 4, 'Kr': 8, 'Rb': 1, 'Sr': 2
        }
        
        total_electrons = 0
        for element, count in atom_counts.items():
            if element in valence_map:
                total_electrons += valence_map[element] * count
            else:
                raise ValueError(f"Unsupported element: {element}")
        
        return total_electrons
    
    @classmethod
    def generate_mol_from_formula(cls, formula: str) -> Chem.Mol:
        """Generate RDKit molecule from formula"""
        try:
            # Expanded SMILES map with many more molecules
            smiles_map = {
                # Simple inorganic molecules
                'H2O': 'O',
                'H2': '[H][H]',
                'O2': 'O=O',
                'N2': 'N#N',
                'CO2': 'O=C=O',
                'CO': '[C-]#[O+]',
                'NO': '[N]=O',
                'NO2': 'O=N=O',
                'SO2': 'O=S=O',
                'SO3': 'O=S(=O)=O',
                'H2S': 'S',
                'HCl': 'Cl',
                'HF': 'F',
                'HBr': 'Br',
                'HI': 'I',
                'NH3': 'N',
                'PH3': 'P',
                'AsH3': '[AsH3]',
                
                # Alkanes
                'CH4': 'C',
                'C2H6': 'CC',
                'C3H8': 'CCC',
                'C4H10': 'CCCC',
                'C5H12': 'CCCCC',
                'C6H14': 'CCCCCC',
                
                # Alkenes
                'C2H4': 'C=C',
                'C3H6': 'CC=C',
                'C4H8': 'CCC=C',
                
                # Alkynes
                'C2H2': 'C#C',
                'C3H4': 'CC#C',
                'C4H6': 'CCC#C',
                
                # Alcohols
                'CH3OH': 'CO',
                'CH4O': 'CO',  # Methanol alternate formula
                'C2H5OH': 'CCO',
                'C2H6O': 'CCO',  # Ethanol alternate formula
                'C3H7OH': 'CCCO',
                'C3H8O': 'CCCO',  # Propanol alternate formula
                'C4H9OH': 'CCCCO',
                'C4H10O': 'CCCCO',  # Butanol alternate formula
                
                # Aldehydes and Ketones
                'CH2O': 'C=O',  # Formaldehyde
                'C2H4O': 'CC=O',  # Acetaldehyde
                'C3H6O': 'CC(C)=O',  # Acetone
                'C4H8O': 'CCCC=O',  # Butanal
                
                # Carboxylic acids
                'CH2O2': 'C(=O)O',  # Formic acid
                'C2H4O2': 'CC(=O)O',  # Acetic acid
                'C3H6O2': 'CCC(=O)O',  # Propionic acid
                
                # Ethers
                'C2H6O2': 'COC',  # Dimethyl ether
                'C4H10O': 'CCOC',  # Diethyl ether
                
                # Amines
                'CH5N': 'CN',  # Methylamine
                'C2H7N': 'CCN',  # Ethylamine
                'C3H9N': 'CCCN',  # Propylamine
                
                # Halogenated compounds
                'CH3Cl': 'CCl',  # Chloromethane
                'CH2Cl2': 'ClCCl',  # Dichloromethane
                'CHCl3': 'ClC(Cl)Cl',  # Chloroform
                'CCl4': 'ClC(Cl)(Cl)Cl',  # Carbon tetrachloride
                'CF4': 'FC(F)(F)F',  # Carbon tetrafluoride
                'CH3F': 'CF',  # Fluoromethane
                'CH3Br': 'CBr',  # Bromomethane
                'CH3I': 'CI',  # Iodomethane
                
                # Benzene and aromatics
                'C6H6': 'c1ccccc1',  # Benzene
                'C7H8': 'Cc1ccccc1',  # Toluene
                'C6H5OH': 'Oc1ccccc1',  # Phenol
                'C6H5NH2': 'Nc1ccccc1',  # Aniline
                
                # Phosphorus compounds
                'PCl3': 'ClP(Cl)Cl',
                'PCl5': 'ClP(Cl)(Cl)(Cl)Cl',
                'PF3': 'FP(F)F',
                'PF5': 'FP(F)(F)(F)F',
                'POCl3': 'O=P(Cl)(Cl)Cl',
                
                # Boron compounds
                'BF3': 'FB(F)F',
                'BCl3': 'ClB(Cl)Cl',
                'BH3': '[BH3]',
                'B2H6': 'B1HBH1',  # Diborane
                
                # Sulfur compounds
                'SF4': 'FS(F)(F)F',
                'SF6': 'FS(F)(F)(F)(F)F',
                'H2SO4': 'OS(O)(=O)=O',
                'SCl2': 'ClSCl',
                
                # Noble gas compounds
                'XeF2': 'F[Xe]F',
                'XeF4': 'F[Xe](F)(F)F',
                'XeF6': 'F[Xe](F)(F)(F)(F)F',
                'XeO3': 'O=[Xe](=O)=O',
                
                # Other interesting molecules
                'ClF3': 'FCl(F)F',
                'ClF5': 'FCl(F)(F)(F)F',
                'IF5': 'FI(F)(F)(F)F',
                'IF7': 'FI(F)(F)(F)(F)(F)F',
                'N2O': 'N#[N+][O-]',  # Nitrous oxide
                'N2O4': 'O=N(=O)N(=O)=O',  # Dinitrogen tetroxide
                'N2O5': 'O=N(=O)ON(=O)=O',  # Dinitrogen pentoxide
                'O3': 'O=O[O]',  # Ozone
                'H2O2': 'OO',  # Hydrogen peroxide
                
                # Simple ionic compounds
                'MgBr2': 'Br[Mg]Br',
                'CaCl2': 'Cl[Ca]Cl',
                'NaCl': '[Na+].[Cl-]',
                'KBr': '[K+].[Br-]',
                'MgO': '[Mg+2].[O-2]',
                'CaO': '[Ca+2].[O-2]',
                'Na2O': '[Na+].[Na+].[O-2]',
                'K2O': '[K+].[K+].[O-2]',
                'AlCl3': 'ClAl(Cl)Cl',
                'FeCl3': 'Cl[Fe](Cl)Cl',
                'FeCl2': 'Cl[Fe]Cl',
                'CuSO4': '[Cu+2].[O-]S(=O)(=O)[O-]',
                'CuCl2': 'Cl[Cu]Cl',
                
                # Iron oxides and hydroxides
                'Fe2O3': '[Fe+3].[Fe+3].[O-2].[O-2].[O-2]',  # Iron(III) oxide
                'FeO': '[Fe+2].[O-2]',  # Iron(II) oxide
                'Fe3O4': '[Fe+2].[Fe+3].[Fe+3].[O-2].[O-2].[O-2].[O-2]',  # Magnetite
                
                # Other metal oxides
                'Al2O3': '[Al+3].[Al+3].[O-2].[O-2].[O-2]',  # Aluminum oxide
                'TiO2': '[Ti+4].[O-2].[O-2]',  # Titanium dioxide
                'ZnO': '[Zn+2].[O-2]',  # Zinc oxide
                'CuO': '[Cu+2].[O-2]',  # Copper(II) oxide
                'Cu2O': '[Cu+].[Cu+].[O-2]',  # Copper(I) oxide
                'PbO': '[Pb+2].[O-2]',  # Lead(II) oxide
                'PbO2': '[Pb+4].[O-2].[O-2]',  # Lead(IV) oxide
                'SnO2': '[Sn+4].[O-2].[O-2]',  # Tin(IV) oxide
                'MnO2': '[Mn+4].[O-2].[O-2]',  # Manganese dioxide
                'Cr2O3': '[Cr+3].[Cr+3].[O-2].[O-2].[O-2]',  # Chromium(III) oxide
                
                # Carbonates
                'CaCO3': '[Ca+2].[O-]C(=O)[O-]',  # Calcium carbonate
                'Na2CO3': '[Na+].[Na+].[O-]C(=O)[O-]',  # Sodium carbonate
                'K2CO3': '[K+].[K+].[O-]C(=O)[O-]',  # Potassium carbonate
                'MgCO3': '[Mg+2].[O-]C(=O)[O-]',  # Magnesium carbonate
                
                # Sulfates
                'Na2SO4': '[Na+].[Na+].[O-]S(=O)(=O)[O-]',  # Sodium sulfate
                'K2SO4': '[K+].[K+].[O-]S(=O)(=O)[O-]',  # Potassium sulfate
                'MgSO4': '[Mg+2].[O-]S(=O)(=O)[O-]',  # Magnesium sulfate
                'CaSO4': '[Ca+2].[O-]S(=O)(=O)[O-]',  # Calcium sulfate
                'FeSO4': '[Fe+2].[O-]S(=O)(=O)[O-]',  # Iron(II) sulfate
                
                # Nitrates
                'NaNO3': '[Na+].[O-]N(=O)=O',  # Sodium nitrate
                'KNO3': '[K+].[O-]N(=O)=O',  # Potassium nitrate
                'Ca(NO3)2': '[Ca+2].[O-]N(=O)=O.[O-]N(=O)=O',  # Calcium nitrate
                'AgNO3': '[Ag+].[O-]N(=O)=O',  # Silver nitrate
                
                # Hydroxides
                'NaOH': '[Na+].[OH-]',  # Sodium hydroxide
                'KOH': '[K+].[OH-]',  # Potassium hydroxide
                'Ca(OH)2': '[Ca+2].[OH-].[OH-]',  # Calcium hydroxide
                'Mg(OH)2': '[Mg+2].[OH-].[OH-]',  # Magnesium hydroxide
                'Al(OH)3': '[Al+3].[OH-].[OH-].[OH-]',  # Aluminum hydroxide
                'Fe(OH)3': '[Fe+3].[OH-].[OH-].[OH-]',  # Iron(III) hydroxide
                'Fe(OH)2': '[Fe+2].[OH-].[OH-]'  # Iron(II) hydroxide
            }
            
            # Try direct lookup first
            if formula in smiles_map:
                smiles = smiles_map[formula]
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    raise ValueError(f"Failed to create molecule from SMILES: {smiles}")
                
                # Add hydrogens
                mol = Chem.AddHs(mol)
                
                # Generate 2D coordinates for better visualization
                AllChem.Compute2DCoords(mol)
                
                # Improve coordinates for simple molecules
                mol = cls.optimize_simple_molecule_coords(mol)
                
                return mol
            
            # Try to parse as SMILES directly if not in map
            # This allows advanced users to input SMILES notation
            if any(char in formula for char in ['(', ')', '[', ']', '=', '#', '@']):
                mol = Chem.MolFromSmiles(formula)
                if mol:
                    mol = Chem.AddHs(mol)
                    AllChem.Compute2DCoords(mol)
                    return mol
            
            # Try basic molecular formula parsing for simple molecules
            # This is experimental and may not work for all molecules
            atom_counts = cls.parse_formula(formula)
            
            # For very simple single-element molecules
            if len(atom_counts) == 1:
                element = list(atom_counts.keys())[0]
                count = atom_counts[element]
                if element == 'H' and count == 2:
                    return Chem.AddHs(Chem.MolFromSmiles('[H][H]'))
                elif element in ['F', 'Cl', 'Br', 'I'] and count == 2:
                    # Diatomic halogens
                    smiles = f'{element}{element}'
                    mol = Chem.MolFromSmiles(smiles)
                    if mol:
                        return Chem.AddHs(mol)
            
            # If nothing works, provide helpful error message
            supported = list(smiles_map.keys())[:20]  # Show first 20 as examples
            raise ValueError(
                f"Cannot generate structure for '{formula}'. "
                f"Try one of these formulas: {', '.join(supported)}... "
                f"or input a valid SMILES string."
            )
            
        except Exception as e:
            raise ValueError(f"Error generating molecule: {str(e)}")
    
    @classmethod
    def optimize_simple_molecule_coords(cls, mol: Chem.Mol) -> Chem.Mol:
        """Optimize coordinates for simple molecules (< 10 atoms)"""
        import math
        
        if mol.GetNumAtoms() >= 10:
            return mol  # Only optimize small molecules
        
        # Get the molecule formula
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
        
        # Define custom layouts for common simple molecules
        custom_layouts = {
            'H2O': {'O': (0, 0), 'H': [(-1.0, -0.5), (1.0, -0.5)]},
            'NH3': {'N': (0, 0), 'H': [(-1.0, -0.5), (1.0, -0.5), (0, 1.0)]},
            'CH4': {'C': (0, 0), 'H': [(-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0)]},
            'CO2': {'C': (0, 0), 'O': [(-1.5, 0), (1.5, 0)]},
            'H2': {'H': [(-0.75, 0), (0.75, 0)]},
            'O2': {'O': [(-0.75, 0), (0.75, 0)]},
            'N2': {'N': [(-0.75, 0), (0.75, 0)]},
            'Cl2': {'Cl': [(-0.75, 0), (0.75, 0)]},
            'HCl': {'H': (-0.75, 0), 'Cl': (0.75, 0)},
            'HF': {'H': (-0.75, 0), 'F': (0.75, 0)},
            'HBr': {'H': (-0.75, 0), 'Br': (0.75, 0)},
            'HI': {'H': (-0.75, 0), 'I': (0.75, 0)},
            'SO2': {'S': (0, 0), 'O': [(-1.2, 0.6), (1.2, 0.6)]},
            'SO3': {'S': (0, 0), 'O': [(0, 1.5), (-1.3, -0.75), (1.3, -0.75)]},
            'PCl3': {'P': (0, 0), 'Cl': [(0, 1.5), (-1.3, -0.75), (1.3, -0.75)]},
            'PCl5': {'P': (0, 0), 'Cl': [(0, 1.5), (-1.5, 0), (1.5, 0), (-0.75, -1.3), (0.75, -1.3)]},
            'SF6': {'S': (0, 0), 'F': [(1.5, 0), (-1.5, 0), (0, 1.5), (0, -1.5), (0.75, 0.75), (-0.75, -0.75)]},
            'BF3': {'B': (0, 0), 'F': [(0, 1.5), (-1.3, -0.75), (1.3, -0.75)]},
            'BeF2': {'Be': (0, 0), 'F': [(-1.5, 0), (1.5, 0)]},
            'XeF2': {'Xe': (0, 0), 'F': [(-1.5, 0), (1.5, 0)]},
            'XeF4': {'Xe': (0, 0), 'F': [(1.5, 0), (-1.5, 0), (0, 1.5), (0, -1.5)]},
        }
        
        # Check if we have a custom layout for this formula
        if formula in custom_layouts:
            layout = custom_layouts[formula]
            conf = mol.GetConformer()
            
            # Apply custom layout
            element_counts = {}
            for i, atom in enumerate(mol.GetAtoms()):
                symbol = atom.GetSymbol()
                if symbol not in element_counts:
                    element_counts[symbol] = 0
                
                if symbol in layout:
                    if isinstance(layout[symbol], tuple):
                        # Single position
                        x, y = layout[symbol]
                    else:
                        # Multiple positions
                        positions = layout[symbol]
                        if element_counts[symbol] < len(positions):
                            x, y = positions[element_counts[symbol]]
                        else:
                            # Fallback to circular
                            angle = 2 * math.pi * i / mol.GetNumAtoms()
                            x = 1.5 * math.cos(angle)
                            y = 1.5 * math.sin(angle)
                    
                    conf.SetAtomPosition(i, (x, y, 0))
                    element_counts[symbol] += 1
            
            return mol
        
        # For other simple molecules, optimize the layout
        if mol.GetNumAtoms() <= 4:
            conf = mol.GetConformer()
            num_atoms = mol.GetNumAtoms()
            
            if num_atoms == 2:
                # Linear molecules
                conf.SetAtomPosition(0, (-0.75, 0, 0))
                conf.SetAtomPosition(1, (0.75, 0, 0))
            elif num_atoms == 3:
                # Check if linear or bent
                # For now, assume bent/triangular
                conf.SetAtomPosition(0, (0, 0, 0))
                conf.SetAtomPosition(1, (-1.0, -0.5, 0))
                conf.SetAtomPosition(2, (1.0, -0.5, 0))
            elif num_atoms == 4:
                # Tetrahedral or square planar
                conf.SetAtomPosition(0, (0, 0, 0))
                conf.SetAtomPosition(1, (1.2, 0, 0))
                conf.SetAtomPosition(2, (-0.6, 1.04, 0))
                conf.SetAtomPosition(3, (-0.6, -1.04, 0))
        
        # Scale coordinates for better visualization
        conf = mol.GetConformer()
        positions = conf.GetPositions()
        
        # Center the molecule
        center = positions.mean(axis=0)
        positions -= center
        
        # Apply optimal scaling
        scale = 1.5  # Adjust this for better visualization
        positions *= scale
        
        # Set the new positions
        for i in range(mol.GetNumAtoms()):
            conf.SetAtomPosition(i, positions[i])
        
        return mol
    
    @classmethod
    def is_ionic_compound(cls, formula: str) -> bool:
        """Check if a compound is ionic based on formula"""
        # List of common ionic compounds
        ionic_patterns = [
            # Metal oxides
            'Fe2O3', 'Fe3O4', 'FeO', 'Al2O3', 'TiO2', 'ZnO', 'CuO', 'Cu2O',
            'PbO', 'PbO2', 'SnO2', 'MnO2', 'Cr2O3', 'MgO', 'CaO', 'Na2O', 'K2O',
            # Halides
            'NaCl', 'KBr', 'CaCl2', 'MgBr2', 'AlCl3', 'FeCl3', 'FeCl2', 'CuCl2',
            # Carbonates
            'CaCO3', 'CCaO3', 'Na2CO3', 'K2CO3', 'MgCO3',
            # Sulfates
            'CuSO4', 'FeSO4', 'Na2SO4', 'K2SO4', 'MgSO4', 'CaSO4',
            # Nitrates
            'NaNO3', 'KNO3', 'Ca(NO3)2', 'AgNO3',
            # Hydroxides
            'NaOH', 'KOH', 'Ca(OH)2', 'Mg(OH)2', 'Al(OH)3', 'Fe(OH)3', 'Fe(OH)2'
        ]
        
        return formula in ionic_patterns
    
    @classmethod
    def generate_ionic_structure(cls, formula: str) -> Dict[str, Any]:
        """Generate structure data for ionic compounds without RDKit"""
        # Parse formula to get atom counts
        atom_counts = cls.parse_formula(formula)
        
        # Define ionic compound data
        ionic_data = {
            # Iron oxides
            'Fe2O3': {'name': 'Iron(III) oxide', 'cations': [('Fe', 3, 2)], 'anions': [('O', -2, 3)]},
            'FeO': {'name': 'Iron(II) oxide', 'cations': [('Fe', 2, 1)], 'anions': [('O', -2, 1)]},
            'Al2O3': {'name': 'Aluminum oxide', 'cations': [('Al', 3, 2)], 'anions': [('O', -2, 3)]},
            'TiO2': {'name': 'Titanium dioxide', 'cations': [('Ti', 4, 1)], 'anions': [('O', -2, 2)]},
            'ZnO': {'name': 'Zinc oxide', 'cations': [('Zn', 2, 1)], 'anions': [('O', -2, 1)]},
            'CuO': {'name': 'Copper(II) oxide', 'cations': [('Cu', 2, 1)], 'anions': [('O', -2, 1)]},
            # Halides
            'NaCl': {'name': 'Sodium chloride', 'cations': [('Na', 1, 1)], 'anions': [('Cl', -1, 1)]},
            'CaCl2': {'name': 'Calcium chloride', 'cations': [('Ca', 2, 1)], 'anions': [('Cl', -1, 2)]},
            'MgBr2': {'name': 'Magnesium bromide', 'cations': [('Mg', 2, 1)], 'anions': [('Br', -1, 2)]},
            'KBr': {'name': 'Potassium bromide', 'cations': [('K', 1, 1)], 'anions': [('Br', -1, 1)]},
            # Carbonates
            'CaCO3': {'name': 'Calcium carbonate', 'cations': [('Ca', 2, 1)], 'anions': [('CO3', -2, 1)]},
            'CCaO3': {'name': 'Calcium carbonate', 'cations': [('Ca', 2, 1)], 'anions': [('CO3', -2, 1)]},
            'Na2CO3': {'name': 'Sodium carbonate', 'cations': [('Na', 1, 2)], 'anions': [('CO3', -2, 1)]},
            # Sulfates
            'CuSO4': {'name': 'Copper sulfate', 'cations': [('Cu', 2, 1)], 'anions': [('SO4', -2, 1)]},
            'FeSO4': {'name': 'Iron(II) sulfate', 'cations': [('Fe', 2, 1)], 'anions': [('SO4', -2, 1)]},
            'MgSO4': {'name': 'Magnesium sulfate', 'cations': [('Mg', 2, 1)], 'anions': [('SO4', -2, 1)]},
            # Hydroxides
            'NaOH': {'name': 'Sodium hydroxide', 'cations': [('Na', 1, 1)], 'anions': [('OH', -1, 1)]},
            'Ca(OH)2': {'name': 'Calcium hydroxide', 'cations': [('Ca', 2, 1)], 'anions': [('OH', -1, 2)]},
        }
        
        if formula not in ionic_data:
            raise ValueError(f"Ionic compound {formula} not in database")
        
        compound = ionic_data[formula]
        
        # Calculate molecular weight
        atomic_weights = {
            'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998,
            'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974,
            'S': 32.06, 'Cl': 35.45, 'K': 39.098, 'Ca': 40.078, 'Ti': 47.867,
            'Fe': 55.845, 'Cu': 63.546, 'Zn': 65.38, 'Br': 79.904, 'Ag': 107.868,
            # Polyatomic ions
            'CO3': 60.009, 'SO4': 96.06, 'OH': 17.007
        }
        
        molecular_weight = 0
        for element, count in atom_counts.items():
            if element in atomic_weights:
                molecular_weight += atomic_weights[element] * count
        
        # Build simplified atom representation for ionic compounds
        atoms = []
        bonds = []  # Ionic compounds don't have covalent bonds
        
        # Create a simple layout - cations on left, anions on right
        x_pos = -2.0
        atom_index = 0
        
        # Add cations
        for element, charge, count in compound['cations']:
            for i in range(count):
                atoms.append({
                    'index': atom_index,
                    'symbol': element,
                    'formal_charge': charge,
                    'lone_pairs': 0,  # Simplified for ionic compounds
                    'hybridization': 'UNSPECIFIED',
                    'position': [x_pos, i * 1.5 - (count - 1) * 0.75]
                })
                atom_index += 1
            x_pos += 1.5
        
        # Add anions
        x_pos = 2.0
        for element, charge, count in compound['anions']:
            for i in range(count):
                atoms.append({
                    'index': atom_index,
                    'symbol': element,
                    'formal_charge': charge,
                    'lone_pairs': 0,  # Simplified for ionic compounds
                    'hybridization': 'UNSPECIFIED',
                    'position': [x_pos, i * 1.5 - (count - 1) * 0.75]
                })
                atom_index += 1
            x_pos += 1.5
        
        # Calculate valence electrons (simplified for ionic compounds)
        total_valence_electrons = cls.get_valence_electrons(atom_counts)
        
        lewis_data = {
            'formula': formula,
            'total_valence_electrons': total_valence_electrons,
            'atom_counts': atom_counts,
            'atoms': atoms,
            'bonds': bonds,  # Empty for ionic compounds
            'molecular_weight': molecular_weight,
            'is_ionic': True,
            'compound_name': compound['name']
        }
        
        # Generate simple MOL block for ionic compounds
        mol_block = f"""Ionic Compound: {formula}
  Generated by ChemsTools

  {len(atoms)}  0  0  0  0  0  0  0  0  0999 V2000
"""
        for atom in atoms:
            x, y = atom['position']
            mol_block += f"  {x:8.4f}  {y:8.4f}    0.0000 {atom['symbol']:2}  0  {atom['formal_charge']:2}  0  0  0  0  0  0  0  0  0  0\n"
        mol_block += "M  END\n"
        
        return {
            'mol_data': mol_block,
            'lewis_data': lewis_data,
            'success': True
        }
    
    @classmethod
    def calculate_formal_charges(cls, mol: Chem.Mol) -> List[int]:
        """Calculate formal charges for each atom"""
        formal_charges = []
        for atom in mol.GetAtoms():
            formal_charges.append(atom.GetFormalCharge())
        return formal_charges
    
    @classmethod
    def get_lone_pairs(cls, mol: Chem.Mol) -> List[int]:
        """Calculate lone pairs for each atom"""
        lone_pairs = []
        
        valence_electrons = {
            'H': 1, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'S': 6, 'Cl': 7, 'P': 5, 'Br': 7, 'I': 7,
            'B': 3, 'Al': 3, 'Si': 4, 'As': 5, 'Se': 6, 'Xe': 8, 'Kr': 8, 'Ar': 8, 'Ne': 8,
            'Li': 1, 'Be': 2, 'Na': 1, 'Mg': 2, 'K': 1, 'Ca': 2, 'Fe': 2, 'Cu': 1, 'Zn': 2
        }
        
        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            if symbol in valence_electrons:
                ve = valence_electrons[symbol]
                bonded_electrons = atom.GetTotalValence()
                formal_charge = atom.GetFormalCharge()
                
                # Lone pairs = (valence_electrons - bonded_electrons + formal_charge) / 2
                lp = max(0, (ve - bonded_electrons + formal_charge) // 2)
                lone_pairs.append(lp)
            else:
                lone_pairs.append(0)
        
        return lone_pairs
    
    @classmethod
    def generate_lewis_structure(cls, formula: str) -> Dict[str, Any]:
        """Generate complete Lewis structure data"""
        try:
            # First check if we have a hardcoded simple structure
            from .simple_structures import get_simple_structure
            simple_struct = get_simple_structure(formula)
            if simple_struct:
                # Generate a simple MOL block for the structure
                mol_block = cls.generate_mol_block_from_lewis(simple_struct)
                return {
                    'mol_data': mol_block,
                    'lewis_data': simple_struct,
                    'success': True
                }
            
            # Check if it's an ionic compound
            if cls.is_ionic_compound(formula):
                return cls.generate_ionic_structure(formula)
            
            # Parse formula
            atom_counts = cls.parse_formula(formula)
            total_valence_electrons = cls.get_valence_electrons(atom_counts)
            
            # Generate molecule
            mol = cls.generate_mol_from_formula(formula)
            
            if mol is None:
                raise ValueError("Could not generate valid molecule")
            
            # Get MOL format
            mol_block = Chem.MolToMolBlock(mol)
            
            # Calculate properties
            formal_charges = cls.calculate_formal_charges(mol)
            lone_pairs = cls.get_lone_pairs(mol)
            
            # Build atom information
            atoms = []
            for i, atom in enumerate(mol.GetAtoms()):
                # Get 2D coordinates - they should be available after Compute2DCoords
                position = [0.0, 0.0]  # Default position
                if mol.GetNumConformers() > 0:
                    conf = mol.GetConformer()
                    pos = conf.GetAtomPosition(i)
                    position = [float(pos.x), float(pos.y)]
                else:
                    # Fallback to simple circular layout
                    import math
                    angle = (2 * math.pi * i) / mol.GetNumAtoms()
                    radius = 2.0
                    position = [radius * math.cos(angle), radius * math.sin(angle)]
                
                atoms.append({
                    'index': i,
                    'symbol': atom.GetSymbol(),
                    'formal_charge': formal_charges[i],
                    'lone_pairs': lone_pairs[i],
                    'hybridization': str(atom.GetHybridization()),
                    'position': position
                })
            
            # Build bond information
            bonds = []
            for bond in mol.GetBonds():
                bonds.append({
                    'begin_atom': bond.GetBeginAtomIdx(),
                    'end_atom': bond.GetEndAtomIdx(),
                    'order': int(bond.GetBondType()),
                    'is_aromatic': bond.GetIsAromatic()
                })
            
            lewis_data = {
                'formula': formula,
                'total_valence_electrons': total_valence_electrons,
                'atom_counts': atom_counts,
                'atoms': atoms,
                'bonds': bonds,
                'molecular_weight': rdMolDescriptors.CalcExactMolWt(mol)
            }
            
            return {
                'mol_data': mol_block,
                'lewis_data': lewis_data,
                'success': True
            }
            
        except Exception as e:
            return {
                'mol_data': None,
                'lewis_data': None,
                'success': False,
                'error': str(e)
            }
    
    @classmethod
    def generate_mol_block_from_lewis(cls, lewis_data: Dict[str, Any]) -> str:
        """Generate MOL block from Lewis structure data"""
        atoms = lewis_data['atoms']
        bonds = lewis_data['bonds']
        
        mol_block = f"""{lewis_data['formula']}
  Generated by ChemsTools

{len(atoms):3d}{len(bonds):3d}  0  0  0  0  0  0  0  0999 V2000
"""
        
        # Add atoms
        for atom in atoms:
            x, y = atom['position']
            symbol = atom['symbol']
            charge = atom['formal_charge']
            mol_block += f"{x:10.4f}{y:10.4f}    0.0000 {symbol:2s}  0{charge:3d}  0  0  0  0  0  0  0  0  0  0\n"
        
        # Add bonds
        for bond in bonds:
            mol_block += f"{bond['begin_atom']+1:3d}{bond['end_atom']+1:3d}{bond['order']:3d}  0\n"
        
        mol_block += "M  END\n"
        return mol_block
