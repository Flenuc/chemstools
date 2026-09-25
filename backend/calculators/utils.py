"""
Utilidades químicas avanzadas para cálculos de pH/pOH.
Constantes químicas:
- KW_TEMPERATURE_CORRECTION: Tabla de Kw vs temperatura
- ACTIVITY_COEFFICIENTS: Coeficientes de actividad comunes
- COMMON_BUFFERS: Datos de sistemas buffer conocidos
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


# Constantes químicas
KW_TEMPERATURE_CORRECTION = {
    0: 0.114e-14,    # Kw a 0°C
    5: 0.185e-14,    # Kw a 5°C
    10: 0.293e-14,   # Kw a 10°C
    15: 0.451e-14,   # Kw a 15°C
    20: 0.681e-14,   # Kw a 20°C
    25: 1.008e-14,   # Kw a 25°C (estándar)
    30: 1.469e-14,   # Kw a 30°C
    35: 2.089e-14,   # Kw a 35°C
    40: 2.919e-14,   # Kw a 40°C
    50: 5.474e-14,   # Kw a 50°C
    60: 9.614e-14,   # Kw a 60°C
    80: 25.04e-14,   # Kw a 80°C
    100: 51.3e-14    # Kw a 100°C
}

ACTIVITY_COEFFICIENTS = {
    'debye_huckel_a': 0.5092,  # A para agua a 25°C
    'debye_huckel_b': 0.3283,  # B para agua a 25°C
    'ion_size_parameter': {
        'H+': 9.0,
        'OH-': 3.5,
        'Na+': 4.0,
        'K+': 3.0,
        'Cl-': 3.0,
        'SO4-2': 4.0,
        'Ca+2': 6.0,
        'Mg+2': 8.0
    }
}

COMMON_BUFFERS = {
    'acetate': {
        'pka': 4.76,
        'weak_acid': 'CH3COOH',
        'conjugate_base': 'CH3COO-',
        'molecular_weight': 60.05,
        'buffer_range': (3.76, 5.76),
        'max_capacity_ph': 4.76
    },
    'phosphate': {
        'pka': 7.21,  # pKa2 del H3PO4
        'weak_acid': 'H2PO4-',
        'conjugate_base': 'HPO4-2',
        'molecular_weight': 95.98,
        'buffer_range': (6.21, 8.21),
        'max_capacity_ph': 7.21
    },
    'tris': {
        'pka': 8.07,
        'weak_acid': 'Tris-H+',
        'conjugate_base': 'Tris',
        'molecular_weight': 121.14,
        'buffer_range': (7.07, 9.07),
        'max_capacity_ph': 8.07
    },
    'carbonate': {
        'pka': 10.33,  # pKa2 del H2CO3
        'weak_acid': 'HCO3-',
        'conjugate_base': 'CO3-2',
        'molecular_weight': 60.01,
        'buffer_range': (9.33, 11.33),
        'max_capacity_ph': 10.33
    },
    'citrate': {
        'pka': 6.40,  # pKa3 del ácido cítrico
        'weak_acid': 'H2Cit-',
        'conjugate_base': 'HCit-2',
        'molecular_weight': 192.12,
        'buffer_range': (5.40, 7.40),
        'max_capacity_ph': 6.40
    }
}


# Decoradores
def parallelize(func):
    """Decorador para cálculos intensivos (placeholder para paralelización futura)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Por ahora solo ejecuta la función, futuro: ThreadPoolExecutor
        return func(*args, **kwargs)
    return wrapper


def cached(ttl_seconds=3600):
    """Decorador para resultados reutilizables."""
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave de cache basada en argumentos
            cache_key = str(args) + str(sorted(kwargs.items()))
            
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator


def monitor_performance(func):
    """Decorador para métricas de rendimiento."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"Function {func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper


# Funciones principales
@monitor_performance
def calculate_ionic_strength(concentrations: List[float], charges: List[int]) -> float:
    """
    Calcula la fuerza iónica usando I = 0.5 * Σ(ci * zi²).
    
    Args:
        concentrations: Lista de concentraciones molares
        charges: Lista de cargas iónicas
        
    Returns:
        float: Fuerza iónica en mol/L
    """
    if len(concentrations) != len(charges):
        raise ValueError("Las listas de concentraciones y cargas deben tener la misma longitud")
    
    ionic_strength = 0.5 * sum(c * z**2 for c, z in zip(concentrations, charges))
    return ionic_strength


@cached(ttl_seconds=1800)
def calculate_activity_coefficient(ionic_strength: float, charge: int, 
                                 temperature: float = 25.0, ion: str = None) -> float:
    """
    Calcula el coeficiente de actividad usando la ecuación de Debye-Hückel extendida.
    
    log γ = -A × z² × √I / (1 + B × a × √I)
    
    Args:
        ionic_strength: Fuerza iónica en mol/L
        charge: Carga del ion
        temperature: Temperatura en °C
        ion: Tipo de ion para obtener parámetro de tamaño específico
        
    Returns:
        float: Coeficiente de actividad
    """
    if ionic_strength == 0:
        return 1.0
    
    # Constantes de Debye-Hückel (valores aproximados para agua a 25°C)
    A = ACTIVITY_COEFFICIENTS['debye_huckel_a']
    B = ACTIVITY_COEFFICIENTS['debye_huckel_b']
    
    # Parámetro de tamaño iónico (Å)
    if ion and ion in ACTIVITY_COEFFICIENTS['ion_size_parameter']:
        a = ACTIVITY_COEFFICIENTS['ion_size_parameter'][ion]
    else:
        # Valor por defecto para iones no especificados
        a = 3.0 if abs(charge) == 1 else 4.0 if abs(charge) == 2 else 5.0
    
    # Corrección de temperatura (simplificada)
    temp_factor = 298.15 / (273.15 + temperature)
    A *= temp_factor**0.5
    
    sqrt_I = math.sqrt(ionic_strength)
    log_gamma = -A * charge**2 * sqrt_I / (1 + B * a * sqrt_I)
    
    gamma = 10**log_gamma
    return gamma


@parallelize
@monitor_performance
def calculate_buffer_capacity(ph: float, buffer_components: List[Dict]) -> float:
    """
    Calcula la capacidad buffer usando:
    β = 2.303 * (Kw/[H+] + [H+] + Σ(αi * (1-αi) * Ci))
    
    Args:
        ph: pH del sistema
        buffer_components: Lista de componentes del buffer con pKa y concentración
        
    Returns:
        float: Capacidad buffer en mol/L/pH
    """
    h_concentration = 10**(-ph)
    kw = 1.0e-14  # Simplificado, podría usar corrección de temperatura
    
    # Términos de agua
    water_term = kw / h_concentration + h_concentration
    
    # Términos de buffer
    buffer_term = 0.0
    for component in buffer_components:
        if 'pka' in component and 'concentration' in component:
            pka = component['pka']
            concentration = component['concentration']
            ka = 10**(-pka)
            
            # Fracción alfa
            alpha = ka / (ka + h_concentration)
            buffer_term += alpha * (1 - alpha) * concentration
    
    beta = 2.303 * (water_term + buffer_term)
    return beta


@cached(ttl_seconds=7200)
def correct_kw_for_temperature(temperature: float) -> float:
    """
    Corrige Kw para la temperatura usando interpolación.
    
    Args:
        temperature: Temperatura en °C
        
    Returns:
        float: Kw corregido para la temperatura
    """
    if temperature in KW_TEMPERATURE_CORRECTION:
        return KW_TEMPERATURE_CORRECTION[temperature]
    
    # Interpolación lineal para temperaturas intermedias
    temps = sorted(KW_TEMPERATURE_CORRECTION.keys())
    
    if temperature < temps[0]:
        return KW_TEMPERATURE_CORRECTION[temps[0]]
    if temperature > temps[-1]:
        return KW_TEMPERATURE_CORRECTION[temps[-1]]
    
    # Encontrar temperaturas adyacentes
    for i in range(len(temps) - 1):
        if temps[i] <= temperature <= temps[i + 1]:
            t1, t2 = temps[i], temps[i + 1]
            kw1, kw2 = KW_TEMPERATURE_CORRECTION[t1], KW_TEMPERATURE_CORRECTION[t2]
            
            # Interpolación lineal
            kw = kw1 + (kw2 - kw1) * (temperature - t1) / (t2 - t1)
            return kw
    
    return 1.0e-14  # Valor por defecto


def calculate_alpha_fractions(ka_values: List[float], ph: float) -> List[float]:
    """
    Calcula las fracciones alfa para ácidos polipróticos.
    
    Args:
        ka_values: Lista de constantes de acidez (Ka1, Ka2, ...)
        ph: pH del sistema
        
    Returns:
        List[float]: Fracciones alfa (α0, α1, α2, ...)
    """
    h_concentration = 10**(-ph)
    
    # Calcular denominador
    denominator = 1.0
    h_power = 1.0
    
    for ka in ka_values:
        h_power *= h_concentration
        denominator += ka / h_power
    
    # Calcular fracciones alfa
    alphas = []
    h_power = 1.0
    
    # α0
    alphas.append(h_power / denominator)
    
    # α1, α2, ...
    for ka in ka_values:
        h_power *= h_concentration / ka
        alphas.append(h_power / denominator)
    
    return alphas


def suggest_buffer_system(target_ph: float) -> Dict[str, any]:
    """
    Recomienda un sistema buffer óptimo para el pH objetivo.
    
    Args:
        target_ph: pH deseado
        
    Returns:
        Dict: Información del buffer recomendado
    """
    best_buffer = None
    min_difference = float('inf')
    
    for name, buffer_info in COMMON_BUFFERS.items():
        pka = buffer_info['pka']
        difference = abs(target_ph - pka)
        
        if difference < min_difference:
            min_difference = difference
            best_buffer = {
                'name': name,
                'pka': pka,
                'range': buffer_info['buffer_range'],
                'difference_from_target': difference,
                'efficiency': max(0, 1 - difference / 2),  # Eficiencia basada en proximidad
                **buffer_info
            }
    
    return best_buffer


@monitor_performance
def comprehensive_ph_calculation(input_data: Dict[str, any]) -> Dict[str, any]:
    """
    Realiza un cálculo comprehensivo de pH con todas las correcciones.
    
    Args:
        input_data: Datos de entrada validados
        
    Returns:
        Dict: Resultados completos del cálculo
    """
    # Extraer parámetros
    calculation_type = input_data['calculation_type']
    input_value = input_data['input_value']
    input_type = input_data['input_type']
    temperature = input_data.get('temperature', 25.0)
    ionic_strength = input_data.get('ionic_strength', 0.0)
    include_activity = input_data.get('include_activity', False)
    
    # Corregir Kw para temperatura
    kw = correct_kw_for_temperature(temperature)
    
    # Cálculos básicos
    if input_type == 'ph':
        ph = input_value
        h_concentration = 10**(-ph)
    elif input_type == 'poh':
        poh = input_value
        oh_concentration = 10**(-poh)
        h_concentration = kw / oh_concentration
        ph = -math.log10(h_concentration)
    elif input_type == 'h_concentration':
        h_concentration = input_value
        ph = -math.log10(h_concentration)
    else:  # oh_concentration
        oh_concentration = input_value
        h_concentration = kw / oh_concentration
        ph = -math.log10(h_concentration)
    
    # Calcular otras variables
    oh_concentration = kw / h_concentration
    poh = -math.log10(oh_concentration)
    
    # Coeficientes de actividad si se solicita
    activity_coefficient_h = 1.0
    activity_coefficient_oh = 1.0
    
    if include_activity and ionic_strength > 0:
        activity_coefficient_h = calculate_activity_coefficient(ionic_strength, 1, temperature, 'H+')
        activity_coefficient_oh = calculate_activity_coefficient(ionic_strength, -1, temperature, 'OH-')
    
    # Resultados
    results = {
        'ph': round(ph, 3),
        'poh': round(poh, 3),
        'h_concentration': h_concentration,
        'oh_concentration': oh_concentration,
        'ionic_strength': ionic_strength,
        'activity_coefficient_h': round(activity_coefficient_h, 4),
        'activity_coefficient_oh': round(activity_coefficient_oh, 4),
        'corrected_kw': kw,
        'temperature': temperature
    }
    
    # Cálculo de capacidad buffer si hay componentes
    buffer_components = input_data.get('buffer_components', [])
    if buffer_components:
        buffer_capacity = calculate_buffer_capacity(ph, buffer_components)
        results['buffer_capacity'] = round(buffer_capacity, 6)
    
    return results


# Funciones auxiliares para exportación
def format_scientific_notation(value: float, precision: int = 3) -> str:
    """Formatea números en notación científica para exportación."""
    if abs(value) >= 1e-3 and abs(value) < 1000:
        return f"{value:.{precision}f}"
    else:
        return f"{value:.{precision}e}"


def validate_chemical_formula(formula: str) -> bool:
    """Valida que una fórmula química tenga formato correcto."""
    import re
    pattern = r'^[A-Z][a-z]?(\d+)?([A-Z][a-z]?(\d+)?)*$'
    return bool(re.match(pattern, formula))