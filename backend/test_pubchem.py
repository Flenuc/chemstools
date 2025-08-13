#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para la integración con PubChem API
"""
import requests
import json
import time
import sys
import io

# Configurar salida UTF-8 para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api/structures"

def test_search_compound(query, query_type=None):
    """Probar búsqueda de compuestos"""
    print(f"\n{'='*60}")
    print(f"Buscando: '{query}'" + (f" (tipo: {query_type})" if query_type else ""))
    print('='*60)
    
    params = {'q': query}
    if query_type:
        params['type'] = query_type
    
    response = requests.get(f"{BASE_URL}/search/", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Compuesto encontrado!")
        print(f"  - Fórmula: {data.get('molecular_formula')}")
        print(f"  - IUPAC: {data.get('iupac_name')}")
        print(f"  - SMILES: {data.get('smiles')}")
        print(f"  - PubChem CID: {data.get('pubchem_cid')}")
        print(f"  - Peso molecular: {data.get('molecular_weight')}")
        if data.get('common_names'):
            print(f"  - Nombres comunes: {', '.join(data['common_names'][:3])}")
    else:
        print(f"[ERROR] Error {response.status_code}: {response.json()}")
    
    return response.status_code == 200

def test_lewis_generation(query, query_type=None):
    """Probar generación de estructura de Lewis"""
    print(f"\n{'='*60}")
    print(f"Generando estructura de Lewis para: '{query}'")
    print('='*60)
    
    data = {'query': query}
    if query_type:
        data['query_type'] = query_type
    
    response = requests.post(f"{BASE_URL}/lewis-generator/", json=data)
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"[OK] Estructura generada!")
        print(f"  - Fórmula: {data.get('formula')}")
        print(f"  - Fuente: {data.get('source', 'N/A')}")
        
        if 'lewis_data' in data:
            lewis = data['lewis_data']
            print(f"  - Átomos: {len(lewis.get('atoms', []))}")
            print(f"  - Enlaces: {len(lewis.get('bonds', []))}")
            
            # Mostrar detalles de átomos
            for i, atom in enumerate(lewis.get('atoms', [])[:3]):
                print(f"    Átomo {i}: {atom['element']} en ({atom['x']:.2f}, {atom['y']:.2f})")
                if atom.get('lone_pairs'):
                    print(f"      - Pares libres: {atom['lone_pairs']}")
        
        if data.get('iupac_name'):
            print(f"  - Nombre IUPAC: {data['iupac_name']}")
        if data.get('pubchem_cid'):
            print(f"  - PubChem CID: {data['pubchem_cid']}")
        if data.get('common_names'):
            print(f"  - Nombres comunes: {', '.join(data['common_names'][:3])}")
    else:
        print(f"[ERROR] Error {response.status_code}: {response.json()}")
    
    return response.status_code in [200, 201]

def test_cached_compounds():
    """Listar compuestos en cache"""
    print(f"\n{'='*60}")
    print("Compuestos en cache")
    print('='*60)
    
    response = requests.get(f"{BASE_URL}/cached-compounds/", params={'limit': 5})
    
    if response.status_code == 200:
        compounds = response.json()
        if compounds:
            print(f"[OK] {len(compounds)} compuestos en cache:")
            for comp in compounds:
                print(f"  - {comp['query']} ({comp['molecular_formula']}) - Accesos: {comp['access_count']}")
        else:
            print("[INFO] No hay compuestos en cache todavía")
    else:
        print(f"[ERROR] Error {response.status_code}: {response.json()}")

def main():
    """Ejecutar pruebas"""
    print("\n" + "="*60)
    print("PRUEBAS DE INTEGRACIÓN CON PUBCHEM API")
    print("="*60)
    
    # Pruebas de búsqueda de compuestos
    test_cases_search = [
        # (query, tipo)
        ("water", None),           # Nombre en inglés
        ("agua", None),           # Nombre en español
        ("H2O", "formula"),       # Fórmula
        ("methane", "name"),      # Metano
        ("CH4", None),           # Fórmula de metano
        ("ethanol", None),       # Etanol
        ("C2H5OH", None),        # Fórmula de etanol
        ("benzene", None),       # Benceno
        ("glucose", None),       # Glucosa
        ("O", "smiles"),        # SMILES del agua
    ]
    
    print("\n" + "="*60)
    print("1. PRUEBAS DE BÚSQUEDA DE COMPUESTOS")
    print("="*60)
    
    for query, query_type in test_cases_search:
        if test_search_compound(query, query_type):
            time.sleep(0.3)  # Respetar rate limit
    
    # Pruebas de generación de estructuras
    print("\n" + "="*60)
    print("2. PRUEBAS DE GENERACIÓN DE ESTRUCTURAS DE LEWIS")
    print("="*60)
    
    test_cases_lewis = [
        "water",        # Por nombre
        "agua",         # En español
        "ammonia",      # Amoníaco
        "CO2",          # Dióxido de carbono
        "sulfuric acid", # Ácido sulfúrico
        "NaCl",         # Sal
        "acetone",      # Acetona
    ]
    
    for query in test_cases_lewis:
        if test_lewis_generation(query):
            time.sleep(0.3)  # Respetar rate limit
    
    # Listar compuestos en cache
    print("\n" + "="*60)
    print("3. COMPUESTOS EN CACHE")
    print("="*60)
    test_cached_compounds()
    
    print("\n" + "="*60)
    print("[OK] PRUEBAS COMPLETADAS")
    print("="*60)

if __name__ == "__main__":
    main()
