"""
Algoritmos específicos para cada método de separación.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import math


class SeparationMethodBase(ABC):
    """Clase base abstracta para todos los métodos de separación."""
    
    def __init__(self, name: str, method_type: str):
        self.name = name
        self.method_type = method_type
    
    @abstractmethod
    def is_applicable(self, components: List[Dict], conditions: Dict) -> bool:
        """Determina si el método es aplicable al sistema."""
        pass
    
    @abstractmethod
    def calculate_efficiency(self, components: List[Dict], conditions: Dict) -> float:
        """Calcula la eficiencia esperada del método."""
        pass
    
    @abstractmethod
    def estimate_time(self, mass: float, conditions: Dict) -> float:
        """Estima el tiempo requerido en horas."""
        pass
    
    @abstractmethod
    def estimate_cost(self, mass: float, conditions: Dict) -> float:
        """Estima el costo relativo (1-100)."""
        pass
    
    @abstractmethod
    def get_required_equipment(self) -> List[str]:
        """Lista el equipo necesario."""
        pass
    
    @abstractmethod
    def get_optimal_conditions(self) -> Dict[str, Any]:
        """Retorna las condiciones óptimas de operación."""
        pass


class TamizacionAlgorithm(SeparationMethodBase):
    """Algoritmo de separación por tamizado."""
    
    def __init__(self):
        super().__init__('Tamización', 'mechanical')
        self.size_ratio_threshold = 10  # Diferencia mínima de tamaño
    
    def is_applicable(self, components: List[Dict], conditions: Dict) -> bool:
        """Verifica si hay suficiente diferencia de tamaños."""
        sizes = [c.get('particle_size', 0) for c in components if c.get('particle_size')]
        if len(sizes) < 2:
            return False
        
        max_size = max(sizes)
        min_size = min(sizes)
        
        if min_size == 0:
            return False
        
        return (max_size / min_size) >= self.size_ratio_threshold
    
    def calculate_efficiency(self, components: List[Dict], conditions: Dict) -> float:
        """Eficiencia basada en la diferencia de tamaños."""
        sizes = [c.get('particle_size', 0) for c in components if c.get('particle_size')]
        
        if len(sizes) < 2:
            return 0.0
        
        max_size = max(sizes)
        min_size = min(sizes)
        
        if min_size == 0:
            return 0.0
        
        ratio = max_size / min_size
        
        # Mayor diferencia = mayor eficiencia
        if ratio >= 100:
            return 0.99
        elif ratio >= 50:
            return 0.97
        elif ratio >= 20:
            return 0.95
        elif ratio >= 10:
            return 0.92
        else:
            return 0.85
    
    def estimate_time(self, mass: float, conditions: Dict) -> float:
        """Tiempo basado en la masa a procesar."""
        # Base: 0.5 horas por kg
        return 0.5 * (mass / 1000)
    
    def estimate_cost(self, mass: float, conditions: Dict) -> float:
        """Costo muy bajo para tamización."""
        # Costo base: 5 unidades por kg
        return min(5 * (mass / 1000), 100)
    
    def get_required_equipment(self) -> List[str]:
        return ['Tamices de diferentes mallas', 'Agitador mecánico (opcional)']
    
    def get_optimal_conditions(self) -> Dict[str, Any]:
        return {
            'humidity': '< 5%',
            'vibration': 'Recomendada',
            'temperature': 'Ambiente'
        }


class MagneticSeparationAlgorithm(SeparationMethodBase):
    """Algoritmo de separación magnética."""
    
    def __init__(self):
        super().__init__('Separación Magnética', 'magnetic')
        self.susceptibility_threshold = 1e-6
    
    def is_applicable(self, components: List[Dict], conditions: Dict) -> bool:
        """Verifica si hay componentes magnéticos."""
        for component in components:
            if component.get('magnetic_susceptibility', 0) > self.susceptibility_threshold:
                return True
        return False
    
    def calculate_efficiency(self, components: List[Dict], conditions: Dict) -> float:
        """Eficiencia basada en la susceptibilidad magnética."""
        magnetic_components = [
            c for c in components 
            if c.get('magnetic_susceptibility', 0) > self.susceptibility_threshold
        ]
        
        if not magnetic_components:
            return 0.0
        
        # Materiales ferromagnéticos: alta eficiencia
        max_susceptibility = max(c.get('magnetic_susceptibility', 0) for c in magnetic_components)
        
        if max_susceptibility > 1e-3:  # Ferromagnético
            return 0.99
        elif max_susceptibility > 1e-5:  # Paramagnético fuerte
            return 0.95
        else:  # Paramagnético débil
            return 0.85
    
    def estimate_time(self, mass: float, conditions: Dict) -> float:
        """Tiempo muy rápido para separación magnética."""
        # Base: 0.2 horas por kg
        return 0.2 * (mass / 1000)
    
    def estimate_cost(self, mass: float, conditions: Dict) -> float:
        """Costo bajo para separación magnética."""
        return min(8 * (mass / 1000), 100)
    
    def get_required_equipment(self) -> List[str]:
        return ['Imán permanente o electroimán', 'Banda transportadora (opcional)']
    
    def get_optimal_conditions(self) -> Dict[str, Any]:
        return {
            'field_strength': '> 0.5 Tesla',
            'particle_size': '< 10 mm',
            'dry_material': True
        }


class FlotationAlgorithm(SeparationMethodBase):
    """Algoritmo de separación por flotación."""
    
    def __init__(self):
        super().__init__('Flotación', 'mechanical')
        self.density_threshold = 0.1  # g/cm³
    
    def is_applicable(self, components: List[Dict], conditions: Dict) -> bool:
        """Verifica diferencias de densidad significativas."""
        densities = [c.get('density', 1.0) for c in components]
        
        if len(densities) < 2:
            return False
        
        max_density = max(densities)
        min_density = min(densities)
        
        return (max_density - min_density) >= self.density_threshold
    
    def calculate_efficiency(self, components: List[Dict], conditions: Dict) -> float:
        """Eficiencia basada en diferencias de densidad."""
        densities = [c.get('density', 1.0) for c in components]
        
        if len(densities) < 2:
            return 0.0
        
        max_density = max(densities)
        min_density = min(densities)
        density_diff = max_density - min_density
        
        # Mayor diferencia = mayor eficiencia
        if density_diff >= 1.0:
            return 0.95
        elif density_diff >= 0.5:
            return 0.90
        elif density_diff >= 0.2:
            return 0.85
        else:
            return 0.75
    
    def estimate_time(self, mass: float, conditions: Dict) -> float:
        """Tiempo moderado para flotación."""
        # Base: 0.5 horas por kg
        return 0.5 * (mass / 1000)
    
    def estimate_cost(self, mass: float, conditions: Dict) -> float:
        """Costo bajo-moderado."""
        return min(10 * (mass / 1000), 100)
    
    def get_required_equipment(self) -> List[str]:
        return ['Tanque de flotación', 'Líquido de flotación', 'Agitador']
    
    def get_optimal_conditions(self) -> Dict[str, Any]:
        return {
            'liquid': 'Agua o solución salina',
            'temperature': '20-25°C',
            'agitation': 'Suave'
        }


class FiltrationAlgorithm(SeparationMethodBase):
    """Algoritmo de filtración sólido-líquido."""
    
    def __init__(self):
        super().__init__('Filtración', 'physical')
    
    def is_applicable(self, components: List[Dict], conditions: Dict) -> bool:
        """Aplicable cuando hay fases sólida y líquida."""
        phases = set(c.get('phase', '') for c in components)
        return 'solid' in phases and 'liquid' in phases
    
    def calculate_efficiency(self, components: List[Dict], conditions: Dict) -> float:
        """Alta eficiencia para filtración bien diseñada."""
        solid_size = min(
            c.get('particle_size', float('inf')) 
            for c in components 
            if c.get('phase') == 'solid'
        )
        
        if solid_size == float('inf'):
            return 0.95
        
        # Partículas más grandes = mayor eficiencia
        if solid_size >= 100:  # μm
            return 0.99
        elif solid_size >= 10:
            return 0.97
        elif solid_size >= 1:
            return 0.95
        else:
            return 0.90
    
    def estimate_time(self, mass: float, conditions: Dict) -> float:
        """Tiempo rápido para filtración."""
        # Base: 0.2 horas por kg
        return 0.2 * (mass / 1000)
    
    def estimate_cost(self, mass: float, conditions: Dict) -> float:
        """Costo muy bajo."""
        return min(3 * (mass / 1000), 100)
    
    def get_required_equipment(self) -> List[str]:
        return ['Papel filtro o membrana', 'Embudo', 'Matraz de vacío (opcional)']
    
    def get_optimal_conditions(self) -> Dict[str, Any]:
        return {
            'filter_pore_size': 'Según tamaño de partícula',
            'vacuum': 'Opcional para acelerar',
            'temperature': 'Ambiente'
        }


class DistillationAlgorithm(SeparationMethodBase):
    """Algoritmo de destilación."""
    
    def __init__(self):
        super().__init__('Destilación', 'thermal')
        self.bp_difference_threshold = 25  # °C
    
    def is_applicable(self, components: List[Dict], conditions: Dict) -> bool:
        """Verifica diferencias de punto de ebullición."""
        boiling_points = [
            c.get('boiling_point') 
            for c in components 
            if c.get('boiling_point') is not None
        ]
        
        if len(boiling_points) < 2:
            return False
        
        max_bp = max(boiling_points)
        min_bp = min(boiling_points)
        
        return (max_bp - min_bp) >= self.bp_difference_threshold
    
    def calculate_efficiency(self, components: List[Dict], conditions: Dict) -> float:
        """Eficiencia basada en diferencia de puntos de ebullición."""
        boiling_points = [
            c.get('boiling_point') 
            for c in components 
            if c.get('boiling_point') is not None
        ]
        
        if len(boiling_points) < 2:
            return 0.0
        
        max_bp = max(boiling_points)
        min_bp = min(boiling_points)
        bp_diff = max_bp - min_bp
        
        # Mayor diferencia = mayor eficiencia
        if bp_diff >= 100:
            return 0.98
        elif bp_diff >= 50:
            return 0.95
        elif bp_diff >= 25:
            return 0.90
        else:
            return 0.80
    
    def estimate_time(self, mass: float, conditions: Dict) -> float:
        """Tiempo considerable para destilación."""
        # Base: 2 horas por kg
        return 2.0 * (mass / 1000)
    
    def estimate_cost(self, mass: float, conditions: Dict) -> float:
        """Costo moderado-alto por energía."""
        return min(25 * (mass / 1000), 100)
    
    def get_required_equipment(self) -> List[str]:
        return [
            'Matraz de destilación',
            'Columna de fraccionamiento',
            'Condensador',
            'Fuente de calor controlada'
        ]
    
    def get_optimal_conditions(self) -> Dict[str, Any]:
        return {
            'heating_rate': 'Controlada',
            'reflux_ratio': 'Según separación deseada',
            'pressure': '1 atm o reducida'
        }


class CrystallizationAlgorithm(SeparationMethodBase):
    """Algoritmo de cristalización."""
    
    def __init__(self):
        super().__init__('Cristalización', 'physical')
        self.solubility_threshold = 10  # g/L
    
    def is_applicable(self, components: List[Dict], conditions: Dict) -> bool:
        """Verifica diferencias de solubilidad."""
        solubilities = [
            c.get('solubility_water', 0) 
            for c in components 
            if c.get('solubility_water') is not None
        ]
        
        if not solubilities:
            return False
        
        # Al menos un componente debe ser soluble
        return any(s > self.solubility_threshold for s in solubilities)
    
    def calculate_efficiency(self, components: List[Dict], conditions: Dict) -> float:
        """Eficiencia basada en diferencias de solubilidad."""
        solubilities = [
            c.get('solubility_water', 0) 
            for c in components 
            if c.get('solubility_water') is not None
        ]
        
        if not solubilities:
            return 0.0
        
        # Componentes con alta diferencia de solubilidad
        max_sol = max(solubilities)
        min_sol = min(solubilities)
        
        if min_sol == 0:
            return 0.95  # Uno insoluble, otro soluble
        
        ratio = max_sol / min_sol
        
        if ratio >= 100:
            return 0.95
        elif ratio >= 10:
            return 0.90
        else:
            return 0.85
    
    def estimate_time(self, mass: float, conditions: Dict) -> float:
        """Tiempo largo para cristalización."""
        # Base: 4 horas por kg
        return 4.0 * (mass / 1000)
    
    def estimate_cost(self, mass: float, conditions: Dict) -> float:
        """Costo moderado."""
        return min(20 * (mass / 1000), 100)
    
    def get_required_equipment(self) -> List[str]:
        return [
            'Cristalizador',
            'Sistema de enfriamiento',
            'Agitador',
            'Sistema de filtración'
        ]
    
    def get_optimal_conditions(self) -> Dict[str, Any]:
        return {
            'cooling_rate': '1-2°C/hora',
            'seeding': 'Recomendado',
            'agitation': 'Suave y constante',
            'supersaturation': '1.05-1.2'
        }


# Diccionario de algoritmos disponibles
SEPARATION_ALGORITHMS = {
    'tamizacion': TamizacionAlgorithm(),
    'magnetic_separation': MagneticSeparationAlgorithm(),
    'flotation': FlotationAlgorithm(),
    'filtration': FiltrationAlgorithm(),
    'distillation': DistillationAlgorithm(),
    'crystallization': CrystallizationAlgorithm(),
}


def get_algorithm(method_name: str) -> SeparationMethodBase:
    """Obtiene una instancia del algoritmo de separación."""
    return SEPARATION_ALGORITHMS.get(method_name.lower())


def evaluate_all_methods(components: List[Dict], 
                        conditions: Dict = None) -> List[Dict]:
    """
    Evalúa todos los métodos disponibles para un sistema.
    
    Returns:
        Lista de métodos aplicables con sus métricas
    """
    if conditions is None:
        conditions = {'temperature': 25, 'pressure': 1}
    
    results = []
    total_mass = sum(c.get('mass', 100) for c in components)
    
    for name, algorithm in SEPARATION_ALGORITHMS.items():
        if algorithm.is_applicable(components, conditions):
            results.append({
                'method': name,
                'type': algorithm.method_type,
                'applicable': True,
                'efficiency': algorithm.calculate_efficiency(components, conditions),
                'time': algorithm.estimate_time(total_mass, conditions),
                'cost': algorithm.estimate_cost(total_mass, conditions),
                'equipment': algorithm.get_required_equipment(),
                'conditions': algorithm.get_optimal_conditions()
            })
    
    # Ordenar por eficiencia
    results.sort(key=lambda x: x['efficiency'], reverse=True)
    
    return results