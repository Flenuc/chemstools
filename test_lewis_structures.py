#!/usr/bin/env python3
"""
Script de prueba para el endpoint de estructuras de Lewis mejorado.
Prueba la generación de estructuras para diferentes tipos de moléculas.
"""

import requests
import json
import time
from typing import Dict, List

# Configuración
BASE_URL = "http://localhost:8000/api/structures"
LEWIS_ENDPOINT = f"{BASE_URL}/lewis-generator/"
LIST_ENDPOINT = BASE_URL + "/"

# Colores para output en terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.END):
    """Imprimir texto con color"""
    print(f"{color}{text}{Colors.END}")

def test_structure_generation(formula: str) -> Dict:
    """Probar la generación de estructura para una fórmula"""
    print(f"\n{Colors.CYAN}Probando fórmula: {Colors.BOLD}{formula}{Colors.END}")
    
    try:
        response = requests.post(
            LEWIS_ENDPOINT,
            json={"formula": formula},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            print_colored(f"✅ Estructura generada exitosamente", Colors.GREEN)
            print(f"   - ID: {data['id']}")
            print(f"   - Peso molecular: {data['lewis_data']['molecular_weight']:.3f} g/mol")
            print(f"   - Electrones de valencia: {data['lewis_data']['total_valence_electrons']}")
            print(f"   - Átomos: {data['lewis_data']['atom_counts']}")
            print(f"   - Número de átomos: {len(data['lewis_data']['atoms'])}")
            print(f"   - Número de enlaces: {len(data['lewis_data']['bonds'])}")
            return data
            
        elif response.status_code == 200:
            data = response.json()
            print_colored(f"✅ Estructura recuperada de caché", Colors.YELLOW)
            print(f"   - ID: {data['id']}")
            print(f"   - Creada: {data['created_at']}")
            return data
            
        else:
            error = response.json()
            print_colored(f"❌ Error: {error.get('error', 'Unknown error')}", Colors.RED)
            if 'details' in error:
                print(f"   Detalles: {error['details']}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_colored(f"❌ Error: No se puede conectar al servidor. ¿Está corriendo Django?", Colors.RED)
        return None
    except Exception as e:
        print_colored(f"❌ Error inesperado: {str(e)}", Colors.RED)
        return None

def test_recent_structures():
    """Obtener estructuras recientes"""
    print(f"\n{Colors.CYAN}Obteniendo estructuras recientes...{Colors.END}")
    
    try:
        response = requests.get(LIST_ENDPOINT)
        
        if response.status_code == 200:
            structures = response.json()
            if structures:
                print_colored(f"✅ Se encontraron {len(structures)} estructuras recientes:", Colors.GREEN)
                for struct in structures[:5]:  # Mostrar solo las primeras 5
                    print(f"   - {struct['formula']} (ID: {struct['id']}, Creada: {struct['created_at']})")
            else:
                print_colored("ℹ️ No hay estructuras guardadas aún", Colors.YELLOW)
            return structures
        else:
            print_colored(f"❌ Error al obtener estructuras: {response.status_code}", Colors.RED)
            return []
            
    except requests.exceptions.ConnectionError:
        print_colored(f"❌ Error: No se puede conectar al servidor", Colors.RED)
        return []
    except Exception as e:
        print_colored(f"❌ Error inesperado: {str(e)}", Colors.RED)
        return []

def main():
    """Función principal de pruebas"""
    print_colored("\n" + "="*60, Colors.BOLD)
    print_colored("PRUEBAS DEL GENERADOR DE ESTRUCTURAS DE LEWIS MEJORADO", Colors.BOLD)
    print_colored("="*60 + "\n", Colors.BOLD)
    
    # Lista de moléculas para probar (diferentes categorías)
    test_molecules = {
        "Moléculas simples": ["H2O", "NH3", "CH4", "CO2", "HCl"],
        "Hidrocarburos": ["C2H6", "C2H4", "C2H2", "C3H8", "C6H6"],
        "Alcoholes": ["CH3OH", "C2H5OH"],
        "Compuestos halogenados": ["CF4", "CHCl3", "PCl3", "SF6"],
        "Compuestos de azufre": ["SO2", "H2SO4"],
        "Compuestos de nitrógeno": ["NO2", "N2O"],
        "Compuestos nobles": ["XeF4"],
        "Otros": ["O3", "H2O2", "BF3"]
    }
    
    results = {
        "success": [],
        "cached": [],
        "failed": []
    }
    
    # Probar cada categoría
    for category, molecules in test_molecules.items():
        print_colored(f"\n{Colors.MAGENTA}{'='*40}{Colors.END}")
        print_colored(f"{Colors.MAGENTA}Categoría: {category}{Colors.END}")
        print_colored(f"{Colors.MAGENTA}{'='*40}{Colors.END}")
        
        for formula in molecules:
            result = test_structure_generation(formula)
            
            if result:
                if result.get('created_at'):
                    # Verificar si es nueva o cacheada por el timestamp
                    results["success"].append(formula)
                else:
                    results["cached"].append(formula)
            else:
                results["failed"].append(formula)
            
            time.sleep(0.5)  # Pequeña pausa entre requests
    
    # Probar estructuras recientes
    print_colored(f"\n{Colors.MAGENTA}{'='*40}{Colors.END}")
    print_colored(f"{Colors.MAGENTA}Estructuras Recientes{Colors.END}")
    print_colored(f"{Colors.MAGENTA}{'='*40}{Colors.END}")
    recent = test_recent_structures()
    
    # Resumen final
    print_colored(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print_colored(f"{Colors.BOLD}RESUMEN DE PRUEBAS{Colors.END}")
    print_colored(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    total_tested = len(results["success"]) + len(results["cached"]) + len(results["failed"])
    print(f"\nTotal de moléculas probadas: {total_tested}")
    print_colored(f"✅ Exitosas: {len(results['success'])}", Colors.GREEN)
    if results["success"]:
        print(f"   {', '.join(results['success'][:10])}{'...' if len(results['success']) > 10 else ''}")
    
    print_colored(f"💾 Recuperadas de caché: {len(results['cached'])}", Colors.YELLOW)
    if results["cached"]:
        print(f"   {', '.join(results['cached'][:10])}{'...' if len(results['cached']) > 10 else ''}")
    
    print_colored(f"❌ Fallidas: {len(results['failed'])}", Colors.RED)
    if results["failed"]:
        print(f"   {', '.join(results['failed'])}")
    
    print_colored(f"\n📊 Estructuras en base de datos: {len(recent)}", Colors.CYAN)
    
    # Calcular tasa de éxito
    if total_tested > 0:
        success_rate = ((len(results["success"]) + len(results["cached"])) / total_tested) * 100
        color = Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 50 else Colors.RED
        print_colored(f"\n🎯 Tasa de éxito: {success_rate:.1f}%", color)
    
    # Probar con SMILES directamente (funcionalidad avanzada)
    print_colored(f"\n{Colors.MAGENTA}{'='*40}{Colors.END}")
    print_colored(f"{Colors.MAGENTA}Prueba Avanzada: SMILES directo{Colors.END}")
    print_colored(f"{Colors.MAGENTA}{'='*40}{Colors.END}")
    
    # Probar con un SMILES de benceno
    smiles_test = "c1ccccc1"  # Benceno en notación SMILES
    print(f"\nProbando con SMILES: {smiles_test}")
    result = test_structure_generation(smiles_test)
    
    if result:
        print_colored("✅ El sistema también acepta notación SMILES!", Colors.GREEN)
    
    print_colored(f"\n{Colors.BOLD}Pruebas completadas!{Colors.END}")

if __name__ == "__main__":
    main()
