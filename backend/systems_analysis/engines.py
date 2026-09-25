"""
Motor de análisis de sistemas químicos con algoritmos inteligentes.
"""
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ComponentData:
    """Datos de un componente del sistema."""
    substance_id: str
    mass_fraction: float
    particle_size: Optional[float] = None
    phase: str = 'solid'


@dataclass
class PhaseData:
    """Datos de una fase del sistema."""
    phase_type: str  # solid, liquid, gas
    components: List[str]
    total_fraction: float
    properties: Dict[str, Any]


@dataclass
class MethodSuggestion:
    """Sugerencia de método de separación."""
    method: str
    target_components: List[str]
    efficiency: float
    difficulty: str
    rationale: str


@dataclass
class AnalysisResult:
    """Resultado del análisis del sistema."""
    system_type: str
    phases: List[PhaseData]
    suggested_methods: List[MethodSuggestion]
    overall_separability: float
    estimated_time: float
    complexity_level: str


class SystemAnalyzer:
    """Motor principal de análisis de sistemas químicos."""
    
    # Constantes para algoritmos de separación
    DENSITY_SEPARATION_THRESHOLD = 0.1  # g/cm³
    SIZE_SEPARATION_RATIO = 10  # veces de diferencia
    MAGNETIC_SUSCEPTIBILITY_THRESHOLD = 1e-6
    SOLUBILITY_DIFFERENCE_THRESHOLD = 10  # g/L
    BOILING_POINT_DIFFERENCE_THRESHOLD = 25  # °C
    
    def __init__(self):
        """Inicializa el analizador con configuración por defecto."""
        self.separation_methods = self._initialize_separation_methods()
        
    def _initialize_separation_methods(self) -> Dict[str, Dict]:
        """Inicializa el catálogo de métodos de separación."""
        return {
            'tamizacion': {
                'type': 'mechanical',
                'criterion': 'particle_size',
                'min_ratio': self.SIZE_SEPARATION_RATIO,
                'efficiency': 0.95,
                'difficulty': 'basic'
            },
            'flotacion': {
                'type': 'mechanical',
                'criterion': 'density',
                'min_difference': self.DENSITY_SEPARATION_THRESHOLD,
                'efficiency': 0.85,
                'difficulty': 'basic'
            },
            'magnetic_separation': {
                'type': 'magnetic',
                'criterion': 'magnetic_susceptibility',
                'threshold': self.MAGNETIC_SUSCEPTIBILITY_THRESHOLD,
                'efficiency': 0.98,
                'difficulty': 'basic'
            },
            'filtration': {
                'type': 'physical',
                'criterion': 'phase',
                'applicable': ['solid-liquid'],
                'efficiency': 0.99,
                'difficulty': 'basic'
            },
            'decantation': {
                'type': 'physical',
                'criterion': 'density_liquid',
                'min_difference': 0.05,
                'efficiency': 0.90,
                'difficulty': 'basic'
            },
            'distillation': {
                'type': 'thermal',
                'criterion': 'boiling_point',
                'min_difference': self.BOILING_POINT_DIFFERENCE_THRESHOLD,
                'efficiency': 0.95,
                'difficulty': 'intermediate'
            },
            'crystallization': {
                'type': 'physical',
                'criterion': 'solubility',
                'min_difference': self.SOLUBILITY_DIFFERENCE_THRESHOLD,
                'efficiency': 0.92,
                'difficulty': 'intermediate'
            },
            'extraction': {
                'type': 'chemical',
                'criterion': 'solubility_selective',
                'efficiency': 0.88,
                'difficulty': 'intermediate'
            },
            'sublimation': {
                'type': 'thermal',
                'criterion': 'sublimation_point',
                'efficiency': 0.95,
                'difficulty': 'advanced'
            },
            'chromatography': {
                'type': 'physical',
                'criterion': 'multiple',
                'efficiency': 0.98,
                'difficulty': 'advanced'
            }
        }
    
    def analyze_mixture(self, components: List[ComponentData], 
                       conditions: Dict[str, float] = None) -> AnalysisResult:
        """
        Analiza una mezcla y sugiere métodos de separación óptimos.
        
        Args:
            components: Lista de componentes con sus propiedades
            conditions: Condiciones del análisis (temperatura, presión)
            
        Returns:
            AnalysisResult con el análisis completo
        """
        if not components:
            raise ValueError("La lista de componentes no puede estar vacía")
        
        # Normalizar fracciones másicas
        total_fraction = sum(c.mass_fraction for c in components)
        if abs(total_fraction - 1.0) > 0.01:
            for c in components:
                c.mass_fraction /= total_fraction
        
        # Detectar fases
        phases = self.detect_phases(components)
        
        # Clasificar homogeneidad
        system_type = self.classify_system_homogeneity(phases)
        
        # Extraer propiedades de separación
        properties = self.extract_separation_properties(components)
        
        # Sugerir métodos de separación
        suggested_methods = self.suggest_separation_methods(properties, phases)
        
        # Calcular métricas globales
        overall_separability = self._calculate_separability_score(
            components, suggested_methods
        )
        estimated_time = self._estimate_total_time(suggested_methods)
        complexity_level = self._determine_complexity_level(suggested_methods)
        
        return AnalysisResult(
            system_type=system_type,
            phases=phases,
            suggested_methods=suggested_methods,
            overall_separability=overall_separability,
            estimated_time=estimated_time,
            complexity_level=complexity_level
        )
    
    def detect_phases(self, components: List[ComponentData]) -> List[PhaseData]:
        """
        Detecta las fases presentes en el sistema.
        
        Args:
            components: Lista de componentes
            
        Returns:
            Lista de fases detectadas
        """
        phases_dict = defaultdict(lambda: {
            'components': [],
            'total_fraction': 0.0,
            'properties': {}
        })
        
        for component in components:
            phase = component.phase
            phases_dict[phase]['components'].append(component.substance_id)
            phases_dict[phase]['total_fraction'] += component.mass_fraction
            
            # Agregar propiedades promedio ponderadas solo si existen
            if component.particle_size is not None:
                if 'avg_particle_size' not in phases_dict[phase]['properties']:
                    phases_dict[phase]['properties']['avg_particle_size'] = 0
                    phases_dict[phase]['properties']['has_particles'] = True
                
                phases_dict[phase]['properties']['avg_particle_size'] += (
                    component.particle_size * component.mass_fraction
                )
        
        # Convertir a lista de PhaseData
        phases = []
        for phase_type, data in phases_dict.items():
            # Normalizar propiedades promedio solo si se calcularon
            if data['properties'].get('has_particles'):
                data['properties']['avg_particle_size'] /= data['total_fraction']
            elif 'avg_particle_size' in data['properties']:
                # Remover avg_particle_size si no hay partículas medidas
                del data['properties']['avg_particle_size']
            
            phases.append(PhaseData(
                phase_type=phase_type,
                components=data['components'],
                total_fraction=data['total_fraction'],
                properties=data['properties']
            ))
        
        return sorted(phases, key=lambda p: p.total_fraction, reverse=True)
    
    def classify_system_homogeneity(self, phases: List[PhaseData]) -> str:
        """
        Clasifica el sistema como homogéneo, heterogéneo o coloidal.
        
        Args:
            phases: Lista de fases detectadas
            
        Returns:
            Tipo de sistema
        """
        if not phases:
            return 'unknown'
        
        # Sistema con una sola fase visible
        if len(phases) == 1:
            return 'homogeneous'
        
        # Verificar si hay dispersiones coloidales
        # Solo verificar fases que tienen tamaño de partícula definido
        has_colloidal = any(
            phase.properties.get('avg_particle_size', float('inf')) < 1000  # < 1000 nm = 1 μm
            for phase in phases
            if 'avg_particle_size' in phase.properties  # Solo verificar si existe la propiedad
        )
        
        if has_colloidal:
            return 'colloidal'
        
        # Sistema con múltiples fases distinguibles
        return 'heterogeneous'
    
    def extract_separation_properties(self, 
                                     components: List[ComponentData]) -> Dict[str, Any]:
        """
        Extrae propiedades relevantes para la separación.
        
        Args:
            components: Lista de componentes
            
        Returns:
            Diccionario de propiedades de separación
        """
        properties = {
            'density_range': {'min': float('inf'), 'max': -float('inf')},
            'size_range': {'min': float('inf'), 'max': -float('inf')},
            'magnetic_components': [],
            'soluble_components': [],
            'phases_present': set(),
            'boiling_points': [],
            'melting_points': []
        }
        
        # Aquí normalmente consultaríamos la base de datos
        # Por ahora usamos valores simulados
        for component in components:
            properties['phases_present'].add(component.phase)
            
            if component.particle_size:
                properties['size_range']['min'] = min(
                    properties['size_range']['min'], 
                    component.particle_size
                )
                properties['size_range']['max'] = max(
                    properties['size_range']['max'], 
                    component.particle_size
                )
            
            # Simular propiedades (en producción, consultar ChemicalSubstance)
            if 'iron' in component.substance_id.lower():
                properties['magnetic_components'].append(component.substance_id)
            
            if 'salt' in component.substance_id.lower() or \
               'sugar' in component.substance_id.lower():
                properties['soluble_components'].append(component.substance_id)
        
        return properties
    
    def suggest_separation_methods(self, 
                                  properties: Dict[str, Any],
                                  phases: List[PhaseData]) -> List[MethodSuggestion]:
        """
        Sugiere métodos de separación óptimos basados en las propiedades.
        
        Args:
            properties: Propiedades del sistema
            phases: Fases detectadas
            
        Returns:
            Lista de sugerencias de métodos
        """
        suggestions = []
        
        # Separación magnética si hay componentes magnéticos
        if properties['magnetic_components']:
            suggestions.append(MethodSuggestion(
                method='magnetic_separation',
                target_components=properties['magnetic_components'],
                efficiency=0.98,
                difficulty='basic',
                rationale='Componentes ferromagnéticos detectados'
            ))
        
        # Tamización si hay diferencia significativa de tamaños
        size_range = properties['size_range']
        if size_range['max'] > 0 and size_range['min'] > 0:
            size_ratio = size_range['max'] / size_range['min']
            if size_ratio >= self.SIZE_SEPARATION_RATIO:
                suggestions.append(MethodSuggestion(
                    method='tamizacion',
                    target_components=['partículas_grandes', 'partículas_pequeñas'],
                    efficiency=0.95,
                    difficulty='basic',
                    rationale=f'Diferencia de tamaño {size_ratio:.1f}x'
                ))
        
        # Filtración para sistemas sólido-líquido
        if 'solid' in properties['phases_present'] and \
           'liquid' in properties['phases_present']:
            suggestions.append(MethodSuggestion(
                method='filtration',
                target_components=['sólidos'],
                efficiency=0.99,
                difficulty='basic',
                rationale='Separación sólido-líquido detectada'
            ))
        
        # Disolución selectiva si hay componentes solubles
        if properties['soluble_components']:
            suggestions.append(MethodSuggestion(
                method='dissolution',
                target_components=properties['soluble_components'],
                efficiency=0.90,
                difficulty='basic',
                rationale='Componentes solubles en agua detectados'
            ))
        
        # Flotación para diferencias de densidad
        if len(phases) > 1:
            suggestions.append(MethodSuggestion(
                method='flotation',
                target_components=['componentes_ligeros'],
                efficiency=0.85,
                difficulty='basic',
                rationale='Múltiples fases con diferentes densidades'
            ))
        
        # Ordenar por eficiencia y dificultad
        suggestions.sort(key=lambda s: (-s.efficiency, s.difficulty))
        
        return suggestions
    
    def generate_separation_sequence(self, 
                                    methods: List[MethodSuggestion]) -> List[Dict]:
        """
        Genera una secuencia optimizada de separación.
        
        Args:
            methods: Lista de métodos sugeridos
            
        Returns:
            Secuencia ordenada de pasos de separación
        """
        sequence = []
        components_remaining = set()
        
        # Ordenar métodos por eficiencia y complejidad
        sorted_methods = sorted(
            methods,
            key=lambda m: (
                m.difficulty == 'basic',  # Priorizar métodos básicos
                -m.efficiency,  # Luego por eficiencia
                m.difficulty == 'intermediate',
                m.difficulty == 'advanced'
            ),
            reverse=True
        )
        
        for i, method in enumerate(sorted_methods):
            step = {
                'step': i + 1,
                'method': method.method,
                'target': method.target_components,
                'efficiency': method.efficiency,
                'difficulty': method.difficulty,
                'rationale': method.rationale,
                'input': 'mixture' if i == 0 else f'output_step_{i}',
                'output': {
                    'separated': method.target_components,
                    'remaining': f'mixture_step_{i+1}'
                }
            }
            sequence.append(step)
        
        return sequence
    
    def calculate_separation_efficiency(self, 
                                       method: str,
                                       properties: Dict,
                                       conditions: Dict = None) -> float:
        """
        Calcula la eficiencia de un método específico.
        
        Args:
            method: Nombre del método
            properties: Propiedades del sistema
            conditions: Condiciones de operación
            
        Returns:
            Eficiencia estimada (0-1)
        """
        base_efficiency = self.separation_methods.get(
            method, {}
        ).get('efficiency', 0.5)
        
        # Ajustar por condiciones
        if conditions:
            temperature = conditions.get('temperature', 25)
            pressure = conditions.get('pressure', 1)
            
            # Penalizar condiciones extremas
            if temperature < 0 or temperature > 100:
                base_efficiency *= 0.9
            if pressure != 1:
                base_efficiency *= 0.95
        
        return min(base_efficiency, 1.0)
    
    def validate_chemical_compatibility(self, 
                                       components: List[ComponentData]) -> Dict:
        """
        Valida la compatibilidad química entre componentes.
        
        Args:
            components: Lista de componentes
            
        Returns:
            Reporte de compatibilidad
        """
        compatibility_report = {
            'compatible': True,
            'warnings': [],
            'incompatibilities': [],
            'safety_concerns': []
        }
        
        # Verificar incompatibilidades conocidas
        component_names = [c.substance_id.lower() for c in components]
        
        # Ácidos y bases
        has_acid = any('acid' in name or 'hcl' in name for name in component_names)
        has_base = any('base' in name or 'naoh' in name for name in component_names)
        
        if has_acid and has_base:
            compatibility_report['warnings'].append(
                'Reacción ácido-base posible - neutralización esperada'
            )
        
        # Oxidantes y reductores
        has_oxidant = any('peroxide' in name or 'kmno4' in name for name in component_names)
        has_reducer = any('metal' in name or 'sulfite' in name for name in component_names)
        
        if has_oxidant and has_reducer:
            compatibility_report['warnings'].append(
                'Reacción redox posible - tomar precauciones'
            )
            compatibility_report['safety_concerns'].append(
                'Posible generación de calor o gases'
            )
        
        return compatibility_report
    
    def _calculate_separability_score(self, 
                                     components: List[ComponentData],
                                     methods: List[MethodSuggestion]) -> float:
        """
        Calcula un score de separabilidad del sistema.
        
        Args:
            components: Componentes del sistema
            methods: Métodos sugeridos
            
        Returns:
            Score de separabilidad (0-1)
        """
        if not methods:
            return 0.0
        
        # Factores que mejoran la separabilidad
        score = 0.0
        
        # Más métodos disponibles = mejor
        score += min(len(methods) / 5, 0.3)  # Hasta 30%
        
        # Métodos de alta eficiencia
        avg_efficiency = sum(m.efficiency for m in methods) / len(methods)
        score += avg_efficiency * 0.4  # Hasta 40%
        
        # Métodos simples disponibles
        basic_methods = sum(1 for m in methods if m.difficulty == 'basic')
        score += min(basic_methods / 3, 0.3)  # Hasta 30%
        
        return min(score, 1.0)
    
    def _estimate_total_time(self, methods: List[MethodSuggestion]) -> float:
        """
        Estima el tiempo total del proceso de separación.
        
        Args:
            methods: Métodos sugeridos
            
        Returns:
            Tiempo estimado en horas
        """
        time_estimates = {
            'tamizacion': 0.5,
            'magnetic_separation': 0.3,
            'filtration': 0.2,
            'flotation': 0.5,
            'dissolution': 1.0,
            'decantation': 1.0,
            'distillation': 2.0,
            'crystallization': 4.0,
            'extraction': 1.5,
            'sublimation': 2.0,
            'chromatography': 3.0
        }
        
        total_time = 0.0
        for method in methods:
            total_time += time_estimates.get(method.method, 1.0)
        
        return total_time
    
    def _determine_complexity_level(self, 
                                   methods: List[MethodSuggestion]) -> str:
        """
        Determina el nivel de complejidad del proceso.
        
        Args:
            methods: Métodos sugeridos
            
        Returns:
            Nivel de complejidad
        """
        if not methods:
            return 'basic'
        
        difficulties = [m.difficulty for m in methods]
        
        if 'advanced' in difficulties:
            return 'advanced'
        elif 'intermediate' in difficulties:
            return 'intermediate'
        else:
            return 'basic'