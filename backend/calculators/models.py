from django.db import models 
from django.contrib.auth import get_user_model 
from core.models import BaseModel 
import uuid 
import json 

User = get_user_model() 

class GlossaryTerm(BaseModel): 
    """ 
    Representa un término en el glosario químico. 
    """ 
    term = models.CharField(max_length=255, unique=True, help_text="El término químico.") 
    definition = models.TextField(help_text="La definición del término.") 
    
    class Meta: 
        verbose_name = "Término del Glosario" 
        verbose_name_plural = "Términos del Glosario" 
        ordering = ['term'] 
        indexes = [
            models.Index(fields=['term']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self): 
        return self.term 


class PHCalculationHistory(BaseModel): 
    """ 
    Modelo para historial de cálculos avanzados de pH/pOH. 
    Almacena todos los cálculos realizados por los usuarios con metadatos completos. 
    """ 
    CALCULATION_TYPE_CHOICES = [ 
        ('ph_to_all', 'pH a todas las variables'), 
        ('concentration_to_ph', 'Concentración a pH'), 
        ('buffer_calculation', 'Cálculo de buffer'), 
        ('ionic_strength', 'Cálculo de fuerza iónica'), 
        ('activity_correction', 'Corrección de actividad'), 
    ] 
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    user = models.ForeignKey( 
        User,  
        on_delete=models.CASCADE,  
        null=True,  
        blank=True, 
        help_text="Usuario que realizó el cálculo (null para usuarios anónimos)" 
    ) 
    calculation_type = models.CharField( 
        max_length=50,  
        choices=CALCULATION_TYPE_CHOICES, 
        help_text="Tipo de cálculo realizado" 
    ) 
    input_data = models.JSONField( 
        help_text="Datos de entrada validados en formato JSON" 
    ) 
    results = models.JSONField( 
        help_text="Todos los resultados calculados en formato JSON" 
    ) 
    calculation_steps = models.JSONField( 
        null=True,  
        blank=True, 
        help_text="Pasos detallados del cálculo (opcional)" 
    ) 
    warnings = models.JSONField( 
        default=list, 
        help_text="Warnings generados durante el cálculo" 
    ) 
    temperature = models.FloatField( 
        default=25.0, 
        help_text="Temperatura del cálculo en °C" 
    ) 
    ionic_strength = models.FloatField( 
        null=True,  
        blank=True, 
        help_text="Fuerza iónica del sistema en mol/L" 
    ) 
    calculation_time_ms = models.IntegerField( 
        help_text="Tiempo de cálculo en milisegundos" 
    ) 
    
    class Meta: 
        verbose_name = "Historial de Cálculo de pH" 
        verbose_name_plural = "Historial de Cálculos de pH" 
        ordering = ['-created_at'] 
        indexes = [ 
            models.Index(fields=['user']), 
            models.Index(fields=['calculation_type']), 
            models.Index(fields=['created_at']), 
            models.Index(fields=['user', 'calculation_type']), 
        ] 
    
    def __str__(self): 
        user_info = f"Usuario {self.user.username}" if self.user else "Anónimo" 
        return f"{user_info} - {self.get_calculation_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}" 
    
    def export_to_dict(self) -> dict: 
        """ 
        Exporta el cálculo a un diccionario para exportación. 
        Returns: 
            dict: Diccionario con todos los datos del cálculo 
        """ 
        return { 
            'id': str(self.id), 
            'calculation_type': self.calculation_type, 
            'calculation_type_display': self.get_calculation_type_display(), 
            'input_data': self.input_data, 
            'results': self.results, 
            'calculation_steps': self.calculation_steps, 
            'warnings': self.warnings, 
            'temperature': self.temperature, 
            'ionic_strength': self.ionic_strength, 
            'calculation_time_ms': self.calculation_time_ms, 
            'created_at': self.created_at.isoformat(), 
            'user': self.user.username if self.user else 'Anónimo' 
        } 
    
    def get_formatted_results(self) -> dict: 
        """ 
        Devuelve resultados formateados para display. 
        Returns: 
            dict: Resultados con formato amigable 
        """ 
        if not self.results: 
            return {} 
        
        formatted = self.results.copy() 
        
        # Formatear concentraciones en notación científica 
        for key in ['h_concentration', 'oh_concentration']: 
            if key in formatted: 
                value = formatted[key] 
                if isinstance(value, (int, float)): 
                    formatted[f"{key}_formatted"] = f"{value:.2e}" 
        
        # Formatear pH y pOH con precisión apropiada 
        for key in ['ph', 'poh']: 
            if key in formatted: 
                value = formatted[key] 
                if isinstance(value, (int, float)): 
                    formatted[f"{key}_formatted"] = f"{value:.2f}" 
        
        return formatted 
    
    def is_buffer_calculation(self) -> bool: 
        """ 
        Determina si este cálculo involucra sistemas buffer. 
        Returns: 
            bool: True si es cálculo de buffer 
        """ 
        return self.calculation_type == 'buffer_calculation' or ( 
            self.input_data and 'buffer_components' in self.input_data 
        ) 
    
    @property 
    def has_warnings(self) -> bool: 
        """Propiedad que indica si el cálculo tiene warnings.""" 
        return bool(self.warnings) 
    
    @property 
    def calculation_duration_seconds(self) -> float: 
        """Duración del cálculo en segundos.""" 
        return self.calculation_time_ms / 1000.0 
    
    @classmethod 
    def get_stats_for_user(cls, user) -> dict: 
        """ 
        Obtiene estadísticas de cálculos para un usuario. 
        Args: 
            user: Usuario para obtener estadísticas 
        Returns: 
            dict: Estadísticas del usuario 
        """ 
        if not user or not user.is_authenticated: 
            return {} 
        
        calculations = cls.objects.filter(user=user) 
        stats = { 
            'total_calculations': calculations.count(), 
            'calculation_types': {}, 
            'average_time_ms': 0, 
            'total_warnings': 0, 
            'buffer_calculations': 0, 
        } 
        
        if stats['total_calculations'] > 0: 
            # Estadísticas por tipo 
            for calc_type, _ in cls.CALCULATION_TYPE_CHOICES: 
                count = calculations.filter(calculation_type=calc_type).count() 
                stats['calculation_types'][calc_type] = count 
            
            # Tiempo promedio 
            avg_time = calculations.aggregate( 
                avg_time=models.Avg('calculation_time_ms') 
            )['avg_time'] 
            stats['average_time_ms'] = round(avg_time or 0, 2) 
            
            # Warnings totales 
            stats['total_warnings'] = sum( 
                len(calc.warnings) for calc in calculations if calc.warnings 
            ) 
            
            # Cálculos de buffer 
            stats['buffer_calculations'] = calculations.filter( 
                calculation_type='buffer_calculation' 
            ).count() 
        
        return stats
    
class ChemicalPreset(BaseModel):
    """
    Modelo para presets predefinidos de soluciones químicas comunes.
    """
    PRESET_CATEGORIES = [
        ('strong_acid', 'Ácido Fuerte'),
        ('strong_base', 'Base Fuerte'),
        ('weak_acid', 'Ácido Débil'),
        ('weak_base', 'Base Débil'),
        ('buffer', 'Sistema Buffer'),
        ('physiological', 'Fisiológico'),
        ('industrial', 'Industrial'),
        ('educational', 'Educacional'),
    ]
    
    CALCULATION_TYPES = [
        ('concentration_to_ph', 'Concentración → pH'),
        ('ph_to_all', 'pH → Todas las variables'),
        ('buffer_calculation', 'Cálculo de Buffer'),
    ]
    
    # Identificación
    code = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Código único del preset (ej: hcl_0.1)"
    )
    name = models.CharField(
        max_length=200,
        help_text="Nombre descriptivo del preset"
    )
    category = models.CharField(
        max_length=20,
        choices=PRESET_CATEGORIES,
        help_text="Categoría del preset"
    )
    
    # Descripción
    description = models.TextField(
        help_text="Descripción detallada del preset y su uso"
    )
    chemical_formula = models.CharField(
        max_length=100,
        blank=True,
        help_text="Fórmula química (ej: HCl, NaOH, CH₃COOH)"
    )
    
    # Datos del cálculo
    calculation_type = models.CharField(
        max_length=30,
        choices=CALCULATION_TYPES,
        help_text="Tipo de cálculo predefinido"
    )
    calculation_values = models.JSONField(
        help_text="Valores predefinidos para el cálculo",
        default=dict
    )
    
    # Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Si el preset está activo y disponible"
    )
    usage_count = models.IntegerField(
        default=0,
        help_text="Contador de veces que se ha usado este preset"
    )
    difficulty_level = models.IntegerField(
        default=1,
        help_text="Nivel de dificultad (1=Básico, 2=Intermedio, 3=Avanzado)"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags para búsqueda y categorización"
    )
    
    class Meta:
        verbose_name = "Preset Químico"
        verbose_name_plural = "Presets Químicos"
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def increment_usage(self):
        """Incrementa el contador de uso."""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def get_calculation_input(self):
        """
        Devuelve los valores formateados para usar en CalculationInput.
        """
        base_values = {
            'calculation_type': self.calculation_type,
            'temperature': 25.0,
        }
        base_values.update(self.calculation_values)
        return base_values
    

class BufferSystem(BaseModel):
    """
    Modelo para sistemas buffer predefinidos.
    """
    # Identificación
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código único del sistema buffer"
    )
    name = models.CharField(
        max_length=200,
        help_text="Nombre del sistema buffer"
    )
    
    # Componentes químicos
    acid_formula = models.CharField(
        max_length=100,
        help_text="Fórmula del ácido"
    )
    base_formula = models.CharField(
        max_length=100,
        help_text="Fórmula de la base conjugada"
    )
    pka = models.FloatField(
        help_text="pKa del ácido"
    )
    
    # Rangos y propiedades
    effective_ph_min = models.FloatField(
        help_text="pH mínimo efectivo del buffer"
    )
    effective_ph_max = models.FloatField(
        help_text="pH máximo efectivo del buffer"
    )
    optimal_ph = models.FloatField(
        help_text="pH óptimo del buffer (generalmente igual al pKa)"
    )
    
    # Información adicional
    common_uses = models.TextField(
        blank=True,
        help_text="Usos comunes de este sistema buffer"
    )
    preparation_notes = models.TextField(
        blank=True,
        help_text="Notas sobre la preparación del buffer"
    )
    
    # Estado
    is_active = models.BooleanField(
        default=True,
        help_text="Si el sistema buffer está activo"
    )
    usage_count = models.IntegerField(
        default=0,
        help_text="Contador de veces que se ha usado"
    )
    
    class Meta:
        verbose_name = "Sistema Buffer"
        verbose_name_plural = "Sistemas Buffer"
        ordering = ['pka', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['pka']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} (pKa={self.pka})"
    
    def get_effective_range(self):
        """Devuelve el rango efectivo como tupla."""
        return (self.effective_ph_min, self.effective_ph_max)
    
    def is_suitable_for_ph(self, target_ph):
        """Verifica si el buffer es adecuado para un pH objetivo."""
        return self.effective_ph_min <= target_ph <= self.effective_ph_max
    
    def get_suitability_score(self, target_ph):
        """
        Calcula un puntaje de idoneidad para un pH objetivo.
        1.0 = óptimo (pH = pKa)
        0.0 = fuera del rango efectivo
        """
        if not self.is_suitable_for_ph(target_ph):
            return 0.0
        
        # Distancia del pH objetivo al pKa
        distance = abs(target_ph - self.pka)
        
        # Score máximo cuando pH = pKa, disminuye con la distancia
        if distance <= 1.0:
            return 1.0 - (distance * 0.3)  # Disminuye 30% por unidad de pH
        else:
            return 0.4 - (distance - 1.0) * 0.2  # Disminuye más lentamente