#!/usr/bin/env python
"""Prueba de compuestos iónicos con delay para evitar rate limiting"""
import requests
import time

BASE_URL = "http://localhost:8000/api/structures"

def test_compound(query, query_type='formula'):
    """Prueba un compuesto específico"""
    print(f"\nProbando: {query}")
    print("-" * 40)
    
    try:
        # Generar estructura
        response = requests.post(
            f"{BASE_URL}/lewis-generator/",
            json={'query': query, 'query_type': query_type}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"OK: Estructura generada exitosamente")
            print(f"  - Fórmula: {data.get('formula')}")
            print(f"  - Fuente: {data.get('source', 'N/A')}")
            
            if data.get('lewis_data'):
                lewis = data['lewis_data']
                print(f"  - Átomos: {len(lewis.get('atoms', []))}")
                print(f"  - Enlaces: {len(lewis.get('bonds', []))}")
                print(f"  - Peso molecular: {lewis.get('molecular_weight', 0):.2f} g/mol")
                
                # Verificar si es iónico
                if lewis.get('is_ionic'):
                    print(f"  - COMPUESTO IÓNICO")
                    print(f"  - Nombre: {lewis.get('compound_name', 'N/A')}")
        else:
            error_text = response.text[:200]
            print(f"ERROR {response.status_code}: {error_text}")
            
    except Exception as e:
        print(f"ERROR de conexion: {e}")

def main():
    print("=" * 60)
    print("PRUEBA DE COMPUESTOS IÓNICOS CON SOPORTE MEJORADO")
    print("=" * 60)
    
    # Probar algunos compuestos iónicos clave
    ionic_compounds = [
        "Fe2O3",  # Óxido de hierro(III)
        "Al2O3",  # Óxido de aluminio
        "TiO2",   # Dióxido de titanio
        "ZnO",    # Óxido de zinc
        "CuO",    # Óxido de cobre(II)
        "NaCl",   # Cloruro de sodio
        "CaCl2",  # Cloruro de calcio
        "MgBr2",  # Bromuro de magnesio
        "KBr",    # Bromuro de potasio
        "CaCO3",  # Carbonato de calcio
        "Na2CO3", # Carbonato de sodio
        "CuSO4",  # Sulfato de cobre
        "FeSO4",  # Sulfato de hierro(II)
        "MgSO4",  # Sulfato de magnesio
        "NaOH",   # Hidróxido de sodio
        "Ca(OH)2" # Hidróxido de calcio
    ]
    
    print("\n[COMPUESTOS IÓNICOS]")
    for compound in ionic_compounds:
        test_compound(compound)
        # Esperar 1 segundo entre peticiones para evitar rate limiting
        time.sleep(1)
    
    # Probar algunos compuestos covalentes para comparar
    print("\n[COMPUESTOS COVALENTES PARA COMPARACIÓN]")
    covalent_compounds = ["H2O", "CH4", "NH3", "CO2"]
    for compound in covalent_compounds:
        test_compound(compound)
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("[OK] PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()
