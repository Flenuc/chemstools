#!/usr/bin/env python
"""Prueba simple de integración con PubChem"""
import requests
import json

BASE_URL = "http://localhost:8000/api/structures"

# Prueba 1: Buscar agua por nombre
print("\n1. Buscando 'water' en PubChem...")
try:
    response = requests.get(f"{BASE_URL}/search/", params={'q': 'water'})
    if response.status_code == 200:
        data = response.json()
        print(f"   OK: Encontrado - Formula: {data.get('molecular_formula')}, SMILES: {data.get('smiles')}")
    else:
        print(f"   Error {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Prueba 2: Generar estructura de Lewis para H2O
print("\n2. Generando estructura Lewis para 'H2O'...")
try:
    response = requests.post(f"{BASE_URL}/lewis-generator/", json={'query': 'H2O'})
    if response.status_code in [200, 201]:
        data = response.json()
        lewis = data.get('lewis_data', {})
        print(f"   OK: Estructura generada")
        print(f"   - Formula: {data.get('formula')}")
        print(f"   - Atomos: {len(lewis.get('atoms', []))}")
        print(f"   - Enlaces: {len(lewis.get('bonds', []))}")
        print(f"   - Fuente: {data.get('source', 'N/A')}")
    else:
        print(f"   Error {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Prueba 3: Buscar por nombre en español
print("\n3. Buscando 'agua' (español)...")
try:
    response = requests.post(f"{BASE_URL}/lewis-generator/", json={'query': 'agua'})
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"   OK: Encontrado y generado")
        print(f"   - Formula: {data.get('formula')}")
        if data.get('iupac_name'):
            print(f"   - IUPAC: {data.get('iupac_name')}")
        if data.get('pubchem_cid'):
            print(f"   - PubChem CID: {data.get('pubchem_cid')}")
    else:
        print(f"   Error {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Prueba 4: Verificar cache
print("\n4. Verificando compuestos en cache...")
try:
    response = requests.get(f"{BASE_URL}/cached-compounds/", params={'limit': 5})
    if response.status_code == 200:
        compounds = response.json()
        if compounds:
            print(f"   OK: {len(compounds)} compuestos en cache")
            for comp in compounds[:3]:
                print(f"   - {comp['query']} ({comp['molecular_formula']})")
        else:
            print("   INFO: Cache vacio")
    else:
        print(f"   Error {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

print("\nPruebas completadas!")
