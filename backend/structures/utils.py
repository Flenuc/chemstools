import json
from typing import Dict, Any, Tuple, List
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors


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
            'Br': 7, 'I': 7
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
            # For simple molecules, use predefined SMILES (most reliable approach)
            smiles_map = {
                'H2O': 'O',
                'CH4': 'C', 
                'NH3': 'N',
                'H2': '[H][H]',
                'O2': 'O=O',
                'N2': 'N#N',
                'CO2': 'O=C=O',
                'C2H6': 'CC',
                'C2H4': 'C=C',
                'C2H2': 'C#C',
                'HCl': 'Cl',
                'HF': 'F',
                'H2S': 'S',
                'PH3': 'P',
                'CH3OH': 'CO',
                'CH2O': 'C=O',
                'C2H5OH': 'CCO',
                'CH3CH2OH': 'CCO'
            }
            
            if formula in smiles_map:
                smiles = smiles_map[formula]
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    raise ValueError(f"Failed to create molecule from SMILES: {smiles}")
                
                # Add hydrogens
                mol = Chem.AddHs(mol)
                return mol
            
            raise ValueError(f"No method available to generate molecule for formula: {formula}. Currently supported: {list(smiles_map.keys())}")
            
        except Exception as e:
            raise ValueError(f"Error generating molecule: {str(e)}")
    
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
            'H': 1, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'S': 6, 'Cl': 7, 'P': 5, 'Br': 7, 'I': 7
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
                # Get 2D coordinates if available, otherwise use default positions
                position = [0.0, 0.0]  # Default position
                try:
                    if mol.GetNumConformers() > 0:
                        pos = mol.GetConformer().GetAtomPosition(i)
                        position = [float(pos.x), float(pos.y)]
                except:
                    # Fallback to simple layout based on atom index
                    angle = (2 * 3.14159 * i) / mol.GetNumAtoms()
                    radius = 2.0
                    position = [radius * (i % 3), radius * (i // 3)]
                
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