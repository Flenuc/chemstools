#!/usr/bin/env python
"""
Script para probar la optimización de coordenadas para moléculas simples
"""

import os
import sys
import django
import json

# Configurar Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.structures.utils import LewisStructureGenerator

def test_molecule_coordinates(formula):
    """Test coordinates generation for a specific molecule"""
    print(f"\n{'='*50}")
    print(f"Testing: {formula}")
    print('='*50)
    
    try:
        result = LewisStructureGenerator.generate_lewis_structure(formula)
        
        if result['success']:
            lewis_data = result['lewis_data']
            
            print(f"✅ Structure generated successfully")
            print(f"   Molecular weight: {lewis_data['molecular_weight']:.3f} g/mol")
            print(f"   Total atoms: {len(lewis_data['atoms'])}")
            print(f"   Total bonds: {len(lewis_data['bonds'])}")
            
            print("\n📍 Atom Coordinates:")
            for atom in lewis_data['atoms']:
                x, y = atom['position']
                print(f"   {atom['index']:2d}. {atom['symbol']:2s} -> ({x:7.3f}, {y:7.3f})")
                if atom['formal_charge'] != 0:
                    print(f"       Formal charge: {atom['formal_charge']:+d}")
                if atom['lone_pairs'] > 0:
                    print(f"       Lone pairs: {atom['lone_pairs']}")
            
            # Calculate center of mass
            if lewis_data['atoms']:
                avg_x = sum(a['position'][0] for a in lewis_data['atoms']) / len(lewis_data['atoms'])
                avg_y = sum(a['position'][1] for a in lewis_data['atoms']) / len(lewis_data['atoms'])
                print(f"\n📊 Center of mass: ({avg_x:.3f}, {avg_y:.3f})")
                
                # Check if coordinates are well distributed
                max_x = max(a['position'][0] for a in lewis_data['atoms'])
                min_x = min(a['position'][0] for a in lewis_data['atoms'])
                max_y = max(a['position'][1] for a in lewis_data['atoms'])
                min_y = min(a['position'][1] for a in lewis_data['atoms'])
                
                spread_x = max_x - min_x
                spread_y = max_y - min_y
                
                print(f"   X range: [{min_x:.3f}, {max_x:.3f}] (spread: {spread_x:.3f})")
                print(f"   Y range: [{min_y:.3f}, {max_y:.3f}] (spread: {spread_y:.3f})")
                
                # Check if coordinates are reasonable
                if spread_x < 0.1 and spread_y < 0.1:
                    print("   ⚠️  Atoms might be too close together")
                elif spread_x > 10 or spread_y > 10:
                    print("   ⚠️  Atoms might be too spread out")
                else:
                    print("   ✅ Coordinate distribution looks good")
            
            return True
        else:
            print(f"❌ Failed to generate structure: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("COORDINATE OPTIMIZATION TEST FOR SIMPLE MOLECULES")
    print("="*60)
    
    # Test molecules with expected custom layouts
    test_molecules = [
        # Simple molecules with custom layouts
        'H2O',    # Water - bent structure
        'NH3',    # Ammonia - pyramidal
        'CH4',    # Methane - tetrahedral
        'CO2',    # Carbon dioxide - linear
        'H2',     # Hydrogen - linear
        'O2',     # Oxygen - linear
        'N2',     # Nitrogen - linear
        'HCl',    # Hydrogen chloride - linear
        'SO2',    # Sulfur dioxide - bent
        'BF3',    # Boron trifluoride - trigonal planar
        'PCl3',   # Phosphorus trichloride - pyramidal
        'SF6',    # Sulfur hexafluoride - octahedral
        
        # Test other small molecules
        'H2O2',   # Hydrogen peroxide
        'C2H4',   # Ethylene
        'C2H2',   # Acetylene
    ]
    
    success_count = 0
    failed = []
    
    for formula in test_molecules:
        if test_molecule_coordinates(formula):
            success_count += 1
        else:
            failed.append(formula)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total tested: {len(test_molecules)}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {len(failed)}")
    
    if failed:
        print(f"\nFailed molecules: {', '.join(failed)}")
    
    success_rate = (success_count / len(test_molecules)) * 100
    print(f"\n🎯 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("✅ Coordinate optimization is working well!")
    elif success_rate >= 60:
        print("⚠️  Coordinate optimization needs some improvements")
    else:
        print("❌ Coordinate optimization needs significant work")

if __name__ == "__main__":
    main()
