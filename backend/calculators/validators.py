"""
Implementa validadores avanzados usando cerberus para cálculos de pH/pOH.
Esquemas requeridos:
- ph_calculation_schema: Para validar entradas de cálculos de pH
- buffer_calculation_schema: Para validar cálculos de buffer
- ionic_strength_schema: Para validar parámetros de fuerza iónica
"""

from cerberus import Validator
from typing import Dict, Any, List, Tuple


class PHValidator(Validator):
    """Validador personalizado para cálculos de pH con reglas químicas específicas."""
    
    def _validate_ph_range(self, constraint, field, value):
        """Valida que el pH esté en un rango químicamente válido."""
        if constraint and not (0 <= value <= 14):
            self._error(field, f"pH debe estar entre 0 y 14, recibido: {value}")
    
    def _validate_concentration_positive(self, constraint, field, value):
        """Valida que las concentraciones sean positivas."""
        if constraint and value <= 0:
            self._error(field, f"La concentración debe ser positiva, recibido: {value}")
    
    def _validate_temperature_range(self, constraint, field, value):
        """Valida que la temperatura esté en un rango físicamente posible."""
        if constraint and not (0 <= value <= 100):
            self._error(field, f"Temperatura debe estar entre 0-100°C, recibido: {value}")


def _validate_ph_input_value(input_type, input_value):
    """Validación específica basada en el tipo de entrada."""
    errors = []
    
    if input_type == 'ph' and not (0 <= input_value <= 14):
        errors.append("pH debe estar entre 0 y 14")
    elif input_type == 'poh' and not (0 <= input_value <= 14):
        errors.append("pOH debe estar entre 0 y 14")
    elif input_type in ['h_concentration', 'oh_concentration'] and input_value <= 0:
        errors.append("Las concentraciones deben ser positivas")
    elif input_type in ['h_concentration', 'oh_concentration'] and input_value > 10:
        errors.append("Concentración muy alta (>10M), revise la entrada")
    
    return errors


# Esquemas de validación
ph_calculation_schema = {
    'calculation_type': {
        'type': 'string',
        'required': True,
        'allowed': ['ph_to_all', 'concentration_to_ph', 'buffer_calculation', 
                   'ionic_strength', 'activity_correction']
    },
    'input_value': {
        'type': 'float',
        'required': True
    },
    'input_type': {
        'type': 'string',
        'required': True,
        'allowed': ['ph', 'poh', 'h_concentration', 'oh_concentration']
    },
    'temperature': {
        'type': 'float',
        'default': 25.0,
        'min': 0,
        'max': 100
    },
    'ionic_strength': {
        'type': 'float',
        'default': 0.0,
        'min': 0,
        'max': 5.0
    },
    'include_activity': {
        'type': 'boolean',
        'default': False
    },
    'show_steps': {
        'type': 'boolean',
        'default': False
    }
}

buffer_calculation_schema = {
    'buffer_components': {
        'type': 'list',
        'required': True,
        'minlength': 1,
        'schema': {
            'type': 'dict',
            'schema': {
                'compound': {
                    'type': 'string',
                    'required': True,
                    'minlength': 1
                },
                'concentration': {
                    'type': 'float',
                    'required': True,
                    'min': 0.0001,  # Concentración mínima práctica
                    'max': 10.0
                },
                'pka': {
                    'type': 'float',
                    'required': False,
                    'min': -2,
                    'max': 16
                }
            }
        }
    },
    'target_ph': {
        'type': 'float',
        'required': False,
        'min': 0,
        'max': 14
    },
    'temperature': {
        'type': 'float',
        'default': 25.0,
        'min': 0,
        'max': 100
    }
}

ionic_strength_schema = {
    'ions': {
        'type': 'list',
        'required': True,
        'minlength': 1,
        'schema': {
            'type': 'dict',
            'schema': {
                'ion': {
                    'type': 'string',
                    'required': True
                },
                'concentration': {
                    'type': 'float',
                    'required': True,
                    'min': 0.0001
                },
                'charge': {
                    'type': 'integer',
                    'required': True,
                    'min': -4,
                    'max': 4,
                    'forbidden': [0]
                }
            }
        }
    },
    'temperature': {
        'type': 'float',
        'default': 25.0,
        'min': 0,
        'max': 100
    }
}


def validate_ph_input(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Valida entrada principal de cálculos de pH.
    
    Returns:
        Tuple[bool, Dict, List]: (es_válido, datos_normalizados, warnings)
    """
    validator = PHValidator(ph_calculation_schema)
    is_valid = validator.validate(data)
    
    # Validación adicional específica por tipo de entrada
    if is_valid and 'input_type' in data and 'input_value' in data:
        specific_errors = _validate_ph_input_value(data['input_type'], data['input_value'])
        if specific_errors:
            validator.errors = {'input_value': specific_errors}
            is_valid = False
    
    warnings = []
    normalized_data = validator.normalized(data) if is_valid else data
    
    if is_valid:
        warnings.extend(generate_warnings(normalized_data))
    
    return is_valid, normalized_data, warnings


def validate_buffer_input(data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Valida entrada de cálculos de buffer.
    
    Returns:
        Tuple[bool, Dict, List]: (es_válido, datos_normalizados, warnings)
    """
    validator = PHValidator(buffer_calculation_schema)
    is_valid = validator.validate(data)
    
    warnings = []
    normalized_data = validator.normalized(data) if is_valid else data
    
    if is_valid:
        warnings.extend(generate_buffer_warnings(normalized_data))
    
    return is_valid, normalized_data, warnings


def validate_concentration_range(field: str, value: float, error_handler) -> bool:
    """
    Custom validator para rangos de concentración.
    
    Args:
        field: Nombre del campo
        value: Valor a validar
        error_handler: Función para manejar errores
        
    Returns:
        bool: True si es válido
    """
    if value <= 0:
        error_handler(field, "La concentración debe ser positiva")
        return False
    
    if value > 10:
        error_handler(field, "Concentración muy alta (>10M), revise la entrada")
        return False
    
    return True


def generate_warnings(data: Dict[str, Any]) -> List[str]:
    """
    Genera warnings químicos contextuales.
    
    Args:
        data: Datos validados
        
    Returns:
        List[str]: Lista de warnings
    """
    warnings = []
    
    # Warnings para pH extremo
    if 'input_value' in data and data.get('input_type') == 'ph':
        ph_value = data['input_value']
        if ph_value < 1:
            warnings.append("pH muy ácido (<1): considere medidas de seguridad")
        elif ph_value > 13:
            warnings.append("pH muy básico (>13): considere medidas de seguridad")
    
    # Warnings para fuerza iónica
    if data.get('ionic_strength', 0) > 1.0:
        warnings.append("Fuerza iónica alta (>1M): los coeficientes de actividad son aproximados")
    
    # Warnings para temperatura
    temp = data.get('temperature', 25.0)
    if temp < 5:
        warnings.append("Temperatura baja: puede afectar la cinética de reacciones")
    elif temp > 80:
        warnings.append("Temperatura alta: puede afectar la estabilidad de compuestos")
    
    return warnings


def generate_buffer_warnings(data: Dict[str, Any]) -> List[str]:
    """
    Genera warnings específicos para cálculos de buffer.
    
    Args:
        data: Datos de buffer validados
        
    Returns:
        List[str]: Lista de warnings específicos de buffer
    """
    warnings = []
    
    components = data.get('buffer_components', [])
    
    # Warning si solo hay un componente
    if len(components) == 1:
        warnings.append("Sistema con un solo componente: capacidad buffer limitada")
    
    # Warning para concentraciones muy diferentes
    concentrations = [comp['concentration'] for comp in components]
    if len(concentrations) > 1:
        max_conc = max(concentrations)
        min_conc = min(concentrations)
        if max_conc / min_conc > 100:
            warnings.append("Concentraciones muy diferentes: buffer poco efectivo")
    
    # Warning para concentraciones muy bajas
    total_concentration = sum(concentrations)
    if total_concentration < 0.01:
        warnings.append("Concentración total baja (<0.01M): capacidad buffer limitada")
    
    return warnings


# Constantes para validación
COMMON_BUFFERS = {
    'acetate': {'pka': 4.76, 'range': (3.76, 5.76)},
    'phosphate': {'pka': 7.21, 'range': (6.21, 8.21)},
    'tris': {'pka': 8.07, 'range': (7.07, 9.07)},
    'carbonate': {'pka': 10.33, 'range': (9.33, 11.33)}
}

ACTIVITY_COEFFICIENT_LIMITS = {
    'low_ionic_strength': 0.1,
    'medium_ionic_strength': 0.5,
    'high_ionic_strength': 1.0
}