#!/usr/bin/env python
"""Test unitario del generador de estructuras iónicas"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from structures.utils import LewisStructureGenerator

def test_ionic_detection():
    """Probar la detección de compuestos iónicos"""
    print("=" * 60)
    print("TEST: DETECCIÓN DE COMPUESTOS IÓNICOS")
    print("=" * 60)
    
    ionic_compounds = ["NaCl", "Fe2O3", "CaCO3", "NaOH", "CuSO4", "MgBr2"]
    covalent_compounds = ["H2O", "CH4", "NH3", "CO2", "C6H6"]
    
    print("\nCompuestos que deberían ser detectados como iónicos:")
    for compound in ionic_compounds:
        is_ionic = LewisStructureGenerator.is_ionic_compound(compound)
        status = "✓ OK" if is_ionic else "✗ FALLO"
        print(f"  {compound}: {is_ionic} {status}")
    
    print("\nCompuestos que NO deberían ser detectados como iónicos:")
    for compound in covalent_compounds:
        is_ionic = LewisStructureGenerator.is_ionic_compound(compound)
        status = "✓ OK" if not is_ionic else "✗ FALLO"
        print(f"  {compound}: {is_ionic} {status}")

def test_ionic_structure_generation():
    """Probar la generación de estructuras iónicas"""
    print("\n" + "=" * 60)
    print("TEST: GENERACIÓN DE ESTRUCTURAS IÓNICAS")
    print("=" * 60)
    
    test_compounds = [
        ("NaCl", "Sodium chloride"),
        ("Fe2O3", "Iron(III) oxide"),
        ("CaCl2", "Calcium chloride"),
        ("Al2O3", "Aluminum oxide"),
        ("CuO", "Copper(II) oxide"),
        ("NaOH", "Sodium hydroxide"),
    ]
    
    for formula, expected_name in test_compounds:
        print(f"\n[{formula}] - {expected_name}")
        print("-" * 40)
        
        try:
            # Generar estructura
            result = LewisStructureGenerator.generate_ionic_structure(formula)
            
            if result['success']:
                lewis = result['lewis_data']
                print(f"  ✓ Estructura generada exitosamente")
                print(f"  - Fórmula: {lewis['formula']}")
                print(f"  - Nombre: {lewis.get('compound_name', 'N/A')}")
                print(f"  - Es iónico: {lewis.get('is_ionic', False)}")
                print(f"  - Átomos: {len(lewis['atoms'])}")
                print(f"  - Enlaces: {len(lewis['bonds'])} (debería ser 0 para iónicos)")
                print(f"  - Peso molecular: {lewis['molecular_weight']:.2f} g/mol")
                
                # Verificar que no hay enlaces (compuestos iónicos)
                if len(lewis['bonds']) == 0:
                    print(f"  ✓ Correctamente sin enlaces covalentes")
                else:
                    print(f"  ✗ ERROR: Se encontraron enlaces en un compuesto iónico")
                
                # Verificar átomos
                print(f"  - Detalles de átomos:")
                for atom in lewis['atoms'][:3]:  # Mostrar solo los primeros 3
                    print(f"    * {atom['symbol']} (carga: {atom['formal_charge']})")
            else:
                print(f"  ✗ Error generando estructura")
                
        except Exception as e:
            print(f"  ✗ Excepción: {e}")

def test_complete_generation():
    """Probar la generación completa (detecta tipo y genera)"""
    print("\n" + "=" * 60)
    print("TEST: GENERACIÓN COMPLETA CON DETECCIÓN AUTOMÁTICA")
    print("=" * 60)
    
    test_compounds = [
        # Iónicos
        ("NaCl", True),
        ("Fe2O3", True),
        ("CaCl2", True),
        # Covalentes
        ("H2O", False),
        ("CH4", False),
        ("NH3", False),
    ]
    
    for formula, should_be_ionic in test_compounds:
        print(f"\n[{formula}] - Esperado {'iónico' if should_be_ionic else 'covalente'}")
        print("-" * 40)
        
        try:
            # Generar estructura usando el método principal
            result = LewisStructureGenerator.generate_lewis_structure(formula)
            
            if result['success']:
                lewis = result['lewis_data']
                is_ionic = lewis.get('is_ionic', False)
                
                print(f"  ✓ Estructura generada")
                print(f"  - Detectado como: {'iónico' if is_ionic else 'covalente'}")
                
                if is_ionic == should_be_ionic:
                    print(f"  ✓ Tipo correctamente detectado")
                else:
                    print(f"  ✗ ERROR: Tipo incorrecto")
                
                print(f"  - Átomos: {len(lewis['atoms'])}")
                print(f"  - Enlaces: {len(lewis['bonds'])}")
                print(f"  - Peso molecular: {lewis['molecular_weight']:.2f} g/mol")
            else:
                print(f"  ✗ Error: {result.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"  ✗ Excepción: {e}")

def main():
    """Ejecutar todas las pruebas"""
    test_ionic_detection()
    test_ionic_structure_generation()
    test_complete_generation()
    
    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()
