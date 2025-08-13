#!/usr/bin/env python
"""
Script para depurar las coordenadas generadas por el backend
"""

import os
import sys
import django
import json

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Intentar importar Django, si falla, usar el módulo directamente
try:
    django.setup()
    from backend.structures.utils import LewisStructureGenerator
except:
    # Si Django falla, importar directamente
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from structures.utils import LewisStructureGenerator

def debug_molecule(formula):
    """Debug coordinates for a specific molecule"""
    print(f"\n{'='*60}")
    print(f"Debugging: {formula}")
    print('='*60)
    
    result = LewisStructureGenerator.generate_lewis_structure(formula)
    
    if result['success']:
        lewis_data = result['lewis_data']
        
        print(f"\n✅ Structure generated successfully")
        print(f"   Formula: {lewis_data['formula']}")
        print(f"   Total atoms: {len(lewis_data['atoms'])}")
        print(f"   Total bonds: {len(lewis_data['bonds'])}")
        
        print("\n📍 ATOMS:")
        print("-" * 50)
        for atom in lewis_data['atoms']:
            print(f"Index {atom['index']:2d}: {atom['symbol']:2s} at position ({atom['position'][0]:7.3f}, {atom['position'][1]:7.3f})")
            print(f"         Charge: {atom['formal_charge']}, Lone pairs: {atom['lone_pairs']}, Hybrid: {atom['hybridization']}")
        
        print("\n🔗 BONDS:")
        print("-" * 50)
        if lewis_data['bonds']:
            for bond in lewis_data['bonds']:
                atom1 = lewis_data['atoms'][bond['begin_atom']]
                atom2 = lewis_data['atoms'][bond['end_atom']]
                print(f"Bond: {atom1['symbol']}(idx:{bond['begin_atom']}) --- {atom2['symbol']}(idx:{bond['end_atom']})  Order: {bond['order']}")
        else:
            print("No bonds (ionic compound?)")
        
        # Check for overlapping atoms
        print("\n⚠️  COORDINATE ANALYSIS:")
        print("-" * 50)
        atoms = lewis_data['atoms']
        for i in range(len(atoms)):
            for j in range(i+1, len(atoms)):
                dist_x = atoms[i]['position'][0] - atoms[j]['position'][0]
                dist_y = atoms[i]['position'][1] - atoms[j]['position'][1]
                distance = (dist_x**2 + dist_y**2)**0.5
                if distance < 0.1:
                    print(f"WARNING: Atoms {i}({atoms[i]['symbol']}) and {j}({atoms[j]['symbol']}) are too close! Distance: {distance:.4f}")
        
        # Print JSON for debugging
        print("\n📋 RAW JSON DATA:")
        print("-" * 50)
        print(json.dumps(lewis_data, indent=2))
        
    else:
        print(f"❌ Failed: {result.get('error', 'Unknown error')}")

def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("COORDINATE DEBUGGING FOR SIMPLE MOLECULES")
    print("="*60)
    
    # Test problematic molecules
    test_molecules = [
        'H2O',    # Water - should be bent
        'NH3',    # Ammonia - pyramidal
        'CH4',    # Methane - tetrahedral
        'CO2',    # Carbon dioxide - linear
    ]
    
    for formula in test_molecules:
        debug_molecule(formula)

if __name__ == "__main__":
    main()
