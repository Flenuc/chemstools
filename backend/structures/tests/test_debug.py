import pytest
from django.test import TestCase
from ..utils import LewisStructureGenerator


class TestDebugLewisGenerator(TestCase):
    """Debug tests to identify the issue"""
    
    def test_debug_water(self):
        """Debug test for water to see actual error"""
        print("Testing H2O generation...")
        result = LewisStructureGenerator.generate_lewis_structure("H2O")
        
        print(f"Success: {result['success']}")
        if not result['success']:
            print(f"Error: {result['error']}")
        else:
            print(f"Lewis data keys: {result['lewis_data'].keys()}")
        
        # This will show us what's happening
        self.assertTrue(result['success'], f"Failed with error: {result.get('error', 'Unknown')}")
    
    def test_debug_rdkit_import(self):
        """Test if RDKit is working properly"""
        try:
            from rdkit import Chem
            print("RDKit imported successfully")
            
            # Test basic RDKit functionality
            mol = Chem.MolFromSmiles('O')
            if mol:
                print("Basic SMILES parsing works")
                mol = Chem.AddHs(mol)
                print(f"Molecule with Hs has {mol.GetNumAtoms()} atoms")
            else:
                print("SMILES parsing failed")
                
            # Test formula parsing
            try:
                mol_formula = Chem.MolFromFormula("H2O")
                print(f"Formula parsing result: {mol_formula}")
            except Exception as e:
                print(f"Formula parsing error: {e}")
                
        except Exception as e:
            print(f"RDKit import/usage error: {e}")
            self.fail(f"RDKit error: {e}")
    
    def test_debug_parse_formula(self):
        """Debug formula parsing"""
        try:
            result = LewisStructureGenerator.parse_formula("H2O")
            print(f"Parse formula result: {result}")
            self.assertEqual(result, {'H': 2, 'O': 1})
        except Exception as e:
            print(f"Parse formula error: {e}")
            self.fail(f"Formula parsing failed: {e}")
    
    def test_debug_valence_electrons(self):
        """Debug valence electron calculation"""
        try:
            atom_counts = {'H': 2, 'O': 1}
            result = LewisStructureGenerator.get_valence_electrons(atom_counts)
            print(f"Valence electrons for H2O: {result}")
            self.assertEqual(result, 8)
        except Exception as e:
            print(f"Valence electron calculation error: {e}")
            self.fail(f"Valence calculation failed: {e}")
    
    def test_debug_mol_generation(self):
        """Debug molecule generation specifically"""
        try:
            print("Testing molecule generation for H2O...")
            mol = LewisStructureGenerator.generate_mol_from_formula("H2O")
            print(f"Generated molecule: {mol}")
            
            if mol:
                print(f"Number of atoms: {mol.GetNumAtoms()}")
                for i, atom in enumerate(mol.GetAtoms()):
                    print(f"Atom {i}: {atom.GetSymbol()}")
            else:
                print("Molecule generation returned None")
                
        except Exception as e:
            print(f"Molecule generation error: {e}")
            self.fail(f"Molecule generation failed: {e}")