"""
Modelos para el Laboratorio Virtual de Análisis de Sistemas Químicos.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class ChemicalSubstance(models.Model):
    """Sustancia química con propiedades físico-químicas completas."""
    
    PHASE_CHOICES = [
        ('solid', 'Sólido'),
        ('liquid', 'Líquido'),
        ('gas', 'Gas'),
    ]
    
    CATEGORY_CHOICES = [
        ('organic', 'Orgánico'),
        ('inorganic', 'Inorgánico'),
        ('metal', 'Metal'),
        ('salt', 'Sal'),
        ('oxide', 'Óxido'),
        ('acid', 'Ácido'),
        ('base', 'Base'),
        ('mineral', 'Mineral'),
    ]
    
    # Identificación
    name = models.CharField(max_length=100, db_index=True)
    formula = models.CharField(max_length=50, db_index=True)
    cas_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    
    # Propiedades básicas
    molecular_weight = models.FloatField(validators=[MinValueValidator(0)])
    density = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Densidad en g/cm³"
    )
    melting_point = models.FloatField(
        null=True, blank=True,
        help_text="Punto de fusión en °C"
    )
    boiling_point = models.FloatField(
        null=True, blank=True,
        help_text="Punto de ebullición en °C"
    )
    
    # Propiedades de separación
    solubility_water = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Solubilidad en agua en g/L a 25°C"
    )
    magnetic_susceptibility = models.FloatField(
        null=True, blank=True,
        help_text="Susceptibilidad magnética en emu/g"
    )
    particle_size_range = models.JSONField(
        default=dict,
        help_text="Rango de tamaño de partícula {min: μm, max: μm}"
    )
    
    # Clasificación
    phase_at_stp = models.CharField(
        max_length=10,
        choices=PHASE_CHOICES,
        db_index=True
    )
    chemical_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    
    # Metadatos
    safety_data = models.JSONField(
        default=dict,
        help_text="Datos de seguridad (toxicidad, inflamabilidad, etc.)"
    )
    color = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sustancia Química"
        verbose_name_plural = "Sustancias Químicas"
        ordering = ['name']
        indexes = [
            models.Index(fields=['phase_at_stp', 'chemical_category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.formula})"
    
    def get_separation_properties(self):
        """Retorna propiedades relevantes para separación."""
        return {
            'density': self.density,
            'solubility': self.solubility_water,
            'magnetic': self.magnetic_susceptibility,
            'particle_size': self.particle_size_range,
            'phase': self.phase_at_stp,
            'melting_point': self.melting_point,
            'boiling_point': self.boiling_point,
        }


class SystemAnalysis(models.Model):
    """Análisis de un sistema químico heterogéneo/homogéneo."""
    
    SYSTEM_TYPES = [
        ('heterogeneous', 'Heterogéneo'),
        ('homogeneous', 'Homogéneo'),
        ('colloidal', 'Coloidal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='system_analyses'
    )
    
    # Identificación
    name = models.CharField(max_length=200)
    components = models.ManyToManyField(
        ChemicalSubstance,
        through='SystemComponent',
        related_name='in_systems'
    )
    
    # Resultados del análisis
    analysis_data = models.JSONField(default=dict)
    system_type = models.CharField(
        max_length=20,
        choices=SYSTEM_TYPES,
        db_index=True
    )
    phases_detected = models.JSONField(
        default=list,
        help_text="Lista de fases detectadas"
    )
    
    # Condiciones
    total_mass = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Masa total del sistema en gramos"
    )
    analysis_temperature = models.FloatField(
        default=25.0,
        help_text="Temperatura de análisis en °C"
    )
    analysis_pressure = models.FloatField(
        default=1.0,
        help_text="Presión de análisis en atm"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Análisis de Sistema"
        verbose_name_plural = "Análisis de Sistemas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['system_type']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_system_type_display()}"
    
    def classify_system_type(self):
        """Clasifica el sistema como heterogéneo u homogéneo."""
        phases = len(self.phases_detected) if self.phases_detected else 0
        if phases > 1:
            return 'heterogeneous'
        elif phases == 1:
            return 'homogeneous'
        else:
            return 'colloidal'
    
    def detect_phases(self):
        """Detecta las fases presentes en el sistema."""
        phases = set()
        for component in self.systemcomponent_set.all():
            phases.add(component.phase)
        return list(phases)


class SystemComponent(models.Model):
    """Componente de un sistema con su fracción y fase."""
    
    PHASE_CHOICES = [
        ('solid', 'Sólido'),
        ('liquid', 'Líquido'),
        ('gas', 'Gas'),
        ('dissolved', 'Disuelto'),
        ('suspended', 'Suspendido'),
        ('emulsified', 'Emulsionado'),
    ]
    
    system = models.ForeignKey(SystemAnalysis, on_delete=models.CASCADE)
    substance = models.ForeignKey(ChemicalSubstance, on_delete=models.CASCADE)
    
    # Proporciones
    mass_fraction = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Fracción másica (0-1)"
    )
    volume_fraction = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Fracción volumétrica (0-1)"
    )
    
    # Estado en el sistema
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES)
    particle_size = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Tamaño de partícula en μm"
    )
    is_dispersed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['system', 'substance']
        ordering = ['-mass_fraction']
    
    def __str__(self):
        return f"{self.substance.name} ({self.mass_fraction:.2%}) en {self.system.name}"


class SeparationMethod(models.Model):
    """Método de separación con criterios y eficiencia."""
    
    METHOD_TYPES = [
        ('mechanical', 'Mecánico'),
        ('physical', 'Físico'),
        ('chemical', 'Químico'),
        ('magnetic', 'Magnético'),
        ('thermal', 'Térmico'),
    ]
    
    COMPLEXITY_LEVELS = [
        ('basic', 'Básico'),
        ('intermediate', 'Intermedio'),
        ('advanced', 'Avanzado'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    description = models.TextField()
    principle = models.TextField(help_text="Principio físico/químico")
    
    # Requisitos
    equipment_required = models.JSONField(
        default=list,
        help_text="Lista de equipos necesarios"
    )
    conditions_required = models.JSONField(
        default=dict,
        help_text="Condiciones necesarias (temp, presión, pH, etc.)"
    )
    
    # Eficiencia
    efficiency_range = models.JSONField(
        default=dict,
        help_text="Rango de eficiencia {min: %, max: %}"
    )
    cost_factor = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Factor de costo (1=barato, 5=caro)"
    )
    complexity_level = models.CharField(
        max_length=20,
        choices=COMPLEXITY_LEVELS
    )
    
    # Aplicabilidad
    applicable_phases = models.JSONField(
        default=list,
        help_text="Fases aplicables"
    )
    property_criteria = models.JSONField(
        default=dict,
        help_text="Criterios de propiedades (tamaño, densidad, etc.)"
    )
    
    class Meta:
        verbose_name = "Método de Separación"
        verbose_name_plural = "Métodos de Separación"
        ordering = ['method_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"


class SeparationProcess(models.Model):
    """Proceso de separación optimizado para un sistema."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    system_analysis = models.ForeignKey(
        SystemAnalysis,
        on_delete=models.CASCADE,
        related_name='separation_processes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Identificación
    process_name = models.CharField(max_length=200)
    separation_steps = models.JSONField(
        default=list,
        help_text="Secuencia ordenada de métodos"
    )
    
    # Métricas
    predicted_efficiency = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Eficiencia predicha en %"
    )
    estimated_time = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Tiempo estimado en horas"
    )
    estimated_cost = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Costo relativo (escala 1-100)"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=SeparationMethod.COMPLEXITY_LEVELS
    )
    
    # Resultados
    final_products = models.JSONField(
        default=list,
        help_text="Productos finales esperados"
    )
    process_diagram = models.JSONField(
        default=dict,
        help_text="Datos para visualización del diagrama"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Proceso de Separación"
        verbose_name_plural = "Procesos de Separación"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.process_name} para {self.system_analysis.name}"
    
    def calculate_overall_efficiency(self):
        """Calcula la eficiencia global del proceso."""
        if not self.separation_steps:
            return 0.0
        
        efficiency = 1.0
        for step in self.separation_steps:
            step_efficiency = step.get('efficiency', 0.8)
            efficiency *= step_efficiency
        
        return efficiency * 100
    
    def generate_process_diagram(self):
        """Genera los datos para el diagrama de flujo."""
        nodes = []
        edges = []
        
        # Nodo inicial
        nodes.append({
            'id': 'start',
            'type': 'input',
            'label': 'Sistema inicial',
            'position': {'x': 0, 'y': 0}
        })
        
        # Nodos de proceso
        for i, step in enumerate(self.separation_steps):
            nodes.append({
                'id': f'step_{i}',
                'type': 'process',
                'label': step.get('method', ''),
                'position': {'x': 200 * (i + 1), 'y': 0}
            })
            
            # Conexiones
            if i == 0:
                edges.append({
                    'source': 'start',
                    'target': f'step_{i}'
                })
            else:
                edges.append({
                    'source': f'step_{i-1}',
                    'target': f'step_{i}'
                })
        
        # Nodos finales
        for i, product in enumerate(self.final_products):
            nodes.append({
                'id': f'product_{i}',
                'type': 'output',
                'label': product.get('name', ''),
                'position': {
                    'x': 200 * (len(self.separation_steps) + 1),
                    'y': 100 * i
                }
            })
            
            if self.separation_steps:
                edges.append({
                    'source': f'step_{len(self.separation_steps)-1}',
                    'target': f'product_{i}'
                })
        
        return {'nodes': nodes, 'edges': edges}


class PropertyDatabase(models.Model):
    """Base de datos extendida de propiedades para sustancias."""
    
    substance = models.OneToOneField(
        ChemicalSubstance,
        on_delete=models.CASCADE,
        related_name='extended_properties'
    )
    
    # Solubilidad
    solubility_organic = models.JSONField(
        default=dict,
        help_text="Solubilidad en solventes orgánicos"
    )
    
    # Propiedades físicas adicionales
    vapor_pressure = models.FloatField(
        null=True, blank=True,
        help_text="Presión de vapor en mmHg a 25°C"
    )
    refractive_index = models.FloatField(null=True, blank=True)
    conductivity = models.FloatField(
        null=True, blank=True,
        help_text="Conductividad en S/m"
    )
    
    # Propiedades mecánicas
    hardness_mohs = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    crystal_system = models.CharField(max_length=50, blank=True)
    
    # Propiedades térmicas
    surface_tension = models.FloatField(
        null=True, blank=True,
        help_text="Tensión superficial en mN/m"
    )
    viscosity = models.FloatField(
        null=True, blank=True,
        help_text="Viscosidad en cP"
    )
    thermal_conductivity = models.FloatField(
        null=True, blank=True,
        help_text="Conductividad térmica en W/m·K"
    )
    specific_heat = models.FloatField(
        null=True, blank=True,
        help_text="Calor específico en J/g·K"
    )
    
    class Meta:
        verbose_name = "Base de Datos de Propiedades"
        verbose_name_plural = "Bases de Datos de Propiedades"
    
    def __str__(self):
        return f"Propiedades extendidas de {self.substance.name}"