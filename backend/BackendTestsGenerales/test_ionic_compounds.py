#!/usr/bin/env python
"""Prueba de compuestos iónicos y complejos"""
import requests
import json

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
            
            if data.get('iupac_name'):
                print(f"  - IUPAC: {data['iupac_name']}")
            if data.get('pubchem_cid'):
                print(f"  - PubChem CID: {data['pubchem_cid']}")
            
            if data.get('lewis_data'):
                lewis = data['lewis_data']
                print(f"  - Átomos: {len(lewis.get('atoms', []))}")
                print(f"  - Enlaces: {len(lewis.get('bonds', []))}")
                print(f"  - Peso molecular: {lewis.get('molecular_weight', 0):.2f} g/mol")
                
                # Mostrar composición
                if lewis.get('atom_counts'):
                    comp = ', '.join([f"{elem}: {count}" for elem, count in lewis['atom_counts'].items()])
                    print(f"  - Composición: {comp}")
        else:
            error_text = response.text[:200]
            print(f"ERROR {response.status_code}: {error_text}")
            
    except Exception as e:
        print(f"ERROR de conexion: {e}")

def main():
    print("=" * 60)
    print("PRUEBA DE COMPUESTOS IÓNICOS Y COMPLEJOS")
    print("=" * 60)
    
    # Óxidos metálicos
    print("\n[OXIDOS METALICOS]")
    test_compound("Fe2O3")  # Óxido de hierro(III)
    test_compound("Al2O3")  # Óxido de aluminio
    test_compound("TiO2")   # Dióxido de titanio
    test_compound("CuO")    # Óxido de cobre(II)
    test_compound("ZnO")    # Óxido de zinc
    
    # Sales simples
    print("\n[SALES SIMPLES]")
    test_compound("NaCl")   # Cloruro de sodio
    test_compound("CaCl2")  # Cloruro de calcio
    test_compound("MgBr2")  # Bromuro de magnesio
    test_compound("KBr")    # Bromuro de potasio
    
    # Carbonatos
    print("\n[CARBONATOS]")
    test_compound("CaCO3")  # Carbonato de calcio
    test_compound("Na2CO3") # Carbonato de sodio
    
    # Sulfatos
    print("\n[SULFATOS]")
    test_compound("CuSO4")  # Sulfato de cobre
    test_compound("FeSO4")  # Sulfato de hierro(II)
    test_compound("MgSO4")  # Sulfato de magnesio
    
    # Hidróxidos
    print("\n[HIDROXIDOS]")
    test_compound("NaOH")   # Hidróxido de sodio
    test_compound("Ca(OH)2") # Hidróxido de calcio
    
    # Búsqueda por nombre
    print("\n[BUSQUEDA POR NOMBRE]")
    test_compound("iron oxide", "name")
    test_compound("limestone", "name")
    test_compound("salt", "name")
    test_compound("baking soda", "name")
    
    print("\n" + "=" * 60)
    print("[OK] PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()
