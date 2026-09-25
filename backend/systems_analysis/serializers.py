"""
Serializers para el sistema de análisis de sistemas químicos.
"""
from rest_framework import serializers
from django.db import transaction
from .models import (
    ChemicalSubstance, SystemAnalysis, SystemComponent,
    SeparationMethod, SeparationProcess, PropertyDatabase
)
from .engines import SystemAnalyzer, ComponentData
import logging

logger = logging.getLogger(__name__)


class ChemicalSubstanceSerializer(serializers.ModelSerializer):
    """Serializer para sustancias químicas."""
    
    separation_properties = serializers.SerializerMethodField()
    
    class Meta:
        model = ChemicalSubstance
        fields = [
            'id', 'name', 'formula', 'cas_number',
            'molecular_weight', 'density',
            'melting_point', 'boiling_point',
            'solubility_water', 'magnetic_susceptibility',
            'particle_size_range', 'phase_at_stp',
            'chemical_category', 'safety_data', 'color',
            'separation_properties'
        ]
        read_only_fields = ['id', 'separation_properties']
    
    def get_separation_properties(self, obj):
        """Obtiene las propiedades relevantes para separación."""
        return obj.get_separation_properties()
    
    def validate_particle_size_range(self, value):
        """Valida el rango de tamaño de partícula."""
        if value:
            if 'min' not in value or 'max' not in value:
                raise serializers.ValidationError(
                    "El rango debe incluir 'min' y 'max'"
                )
            if value['min'] < 0 or value['max'] < 0:
                raise serializers.ValidationError(
                    "Los tamaños no pueden ser negativos"
                )
            if value['min'] > value['max']:
                raise serializers.ValidationError(
                    "El tamaño mínimo no puede ser mayor que el máximo"
                )
        return value


class SystemComponentSerializer(serializers.ModelSerializer):
    """Serializer para componentes del sistema."""
    
    substance_detail = ChemicalSubstanceSerializer(source='substance', read_only=True)
    substance_id = serializers.PrimaryKeyRelatedField(
        queryset=ChemicalSubstance.objects.all(),
        source='substance',
        write_only=True
    )
    
    class Meta:
        model = SystemComponent
        fields = [
            'id', 'substance_id', 'substance_detail',
            'mass_fraction', 'volume_fraction',
            'phase', 'particle_size', 'is_dispersed'
        ]
    
    def validate_mass_fraction(self, value):
        """Valida que la fracción másica esté entre 0 y 1."""
        if not 0 <= value <= 1:
            raise serializers.ValidationError(
                "La fracción másica debe estar entre 0 y 1"
            )
        return value


class SystemAnalysisSerializer(serializers.ModelSerializer):
    """Serializer para análisis de sistemas."""
    
    components_detail = SystemComponentSerializer(
        source='systemcomponent_set',
        many=True,
        read_only=True
    )
    components_input = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    analysis_result = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemAnalysis
        fields = [
            'id', 'name', 'components_detail', 'components_input',
            'analysis_data', 'system_type', 'phases_detected',
            'total_mass', 'analysis_temperature', 'analysis_pressure',
            'analysis_result', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'analysis_data', 'system_type', 'phases_detected',
            'analysis_result', 'created_at', 'updated_at'
        ]
    
    def get_analysis_result(self, obj):
        """Obtiene el resultado del análisis si está disponible."""
        if obj.analysis_data:
            return obj.analysis_data
        return None
    
    def validate_components_input(self, value):
        """Valida los componentes de entrada."""
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos un componente")
        
        total_fraction = sum(c.get('mass_fraction', 0) for c in value)
        if abs(total_fraction - 1.0) > 0.01:
            # Normalizar automáticamente
            for c in value:
                c['mass_fraction'] = c.get('mass_fraction', 0) / total_fraction
        
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        """Crea un análisis y ejecuta el motor de análisis."""
        components_input = validated_data.pop('components_input', [])
        
        # Crear el análisis
        analysis = SystemAnalysis.objects.create(**validated_data)
        
        # Crear los componentes
        for comp_data in components_input:
            substance = ChemicalSubstance.objects.get(
                id=comp_data['substance_id']
            )
            SystemComponent.objects.create(
                system=analysis,
                substance=substance,
                mass_fraction=comp_data['mass_fraction'],
                particle_size=comp_data.get('particle_size'),
                phase=comp_data.get('phase', substance.phase_at_stp),
                is_dispersed=comp_data.get('is_dispersed', False)
            )
        
        # Ejecutar análisis
        self._run_analysis(analysis)
        
        return analysis
    
    def _run_analysis(self, analysis):
        """Ejecuta el motor de análisis."""
        try:
            analyzer = SystemAnalyzer()
            
            # Preparar datos de componentes
            components = []
            for comp in analysis.systemcomponent_set.all():
                components.append(ComponentData(
                    substance_id=comp.substance.name,
                    mass_fraction=comp.mass_fraction,
                    particle_size=comp.particle_size,
                    phase=comp.phase
                ))
            
            # Ejecutar análisis
            conditions = {
                'temperature': analysis.analysis_temperature,
                'pressure': analysis.analysis_pressure
            }
            
            result = analyzer.analyze_mixture(components, conditions)
            
            # Guardar resultados
            analysis.system_type = result.system_type
            analysis.phases_detected = [
                {
                    'phase': p.phase_type,
                    'components': p.components,
                    'total_fraction': p.total_fraction
                }
                for p in result.phases
            ]
            analysis.analysis_data = {
                'system_type': result.system_type,
                'phases': analysis.phases_detected,
                'suggested_methods': [
                    {
                        'method': m.method,
                        'target': m.target_components,
                        'efficiency': m.efficiency,
                        'difficulty': m.difficulty,
                        'rationale': m.rationale
                    }
                    for m in result.suggested_methods
                ],
                'overall_separability': result.overall_separability,
                'estimated_time': result.estimated_time,
                'complexity_level': result.complexity_level
            }
            analysis.save()
            
        except Exception as e:
            logger.error(f"Error en análisis: {e}")
            analysis.analysis_data = {'error': str(e)}
            analysis.save()


class SeparationMethodSerializer(serializers.ModelSerializer):
    """Serializer para métodos de separación."""
    
    class Meta:
        model = SeparationMethod
        fields = '__all__'


class SeparationProcessSerializer(serializers.ModelSerializer):
    """Serializer para procesos de separación."""
    
    system_analysis_detail = SystemAnalysisSerializer(
        source='system_analysis',
        read_only=True
    )
    diagram = serializers.SerializerMethodField()
    
    class Meta:
        model = SeparationProcess
        fields = [
            'id', 'system_analysis', 'system_analysis_detail',
            'process_name', 'separation_steps',
            'predicted_efficiency', 'estimated_time',
            'estimated_cost', 'difficulty_level',
            'final_products', 'process_diagram', 'diagram',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'process_diagram', 'diagram',
            'created_at', 'updated_at'
        ]
    
    def get_diagram(self, obj):
        """Obtiene el diagrama del proceso si está disponible."""
        if hasattr(obj, 'generate_process_diagram'):
            return obj.generate_process_diagram()
        return obj.process_diagram
    
    def create(self, validated_data):
        """Crea un proceso y genera el diagrama."""
        process = super().create(validated_data)
        
        # Generar diagrama
        process.process_diagram = process.generate_process_diagram()
        process.save()
        
        return process


class SystemAnalysisInputSerializer(serializers.Serializer):
    """Serializer para entrada de análisis de sistema."""
    
    name = serializers.CharField(max_length=200)
    components = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    total_mass = serializers.FloatField(min_value=0)
    analysis_conditions = serializers.DictField(required=False)
    
    def validate_components(self, value):
        """Valida la lista de componentes."""
        # Verificar campos requeridos
        for comp in value:
            if 'substance_id' not in comp:
                raise serializers.ValidationError(
                    "Cada componente debe tener 'substance_id'"
                )
            if 'mass_fraction' not in comp:
                raise serializers.ValidationError(
                    "Cada componente debe tener 'mass_fraction'"
                )
        
        # Normalizar fracciones
        total = sum(c['mass_fraction'] for c in value)
        if abs(total - 1.0) > 0.01:
            for c in value:
                c['mass_fraction'] /= total
        
        return value


class SeparationFlowDiagramSerializer(serializers.Serializer):
    """Serializer para generación de diagramas de flujo."""
    
    analysis_id = serializers.UUIDField()
    selected_methods = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    optimization_criteria = serializers.DictField(required=False)
    
    def validate_analysis_id(self, value):
        """Verifica que el análisis exista."""
        try:
            SystemAnalysis.objects.get(id=value)
        except SystemAnalysis.DoesNotExist:
            raise serializers.ValidationError("Análisis no encontrado")
        return value


class SubstanceSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de sustancias."""
    
    query = serializers.CharField(required=False, allow_blank=True)
    phase = serializers.ChoiceField(
        choices=['solid', 'liquid', 'gas'],
        required=False
    )
    category = serializers.ChoiceField(
        choices=[
            'organic', 'inorganic', 'metal', 'salt',
            'oxide', 'acid', 'base', 'mineral'
        ],
        required=False
    )
    min_density = serializers.FloatField(required=False, min_value=0)
    max_density = serializers.FloatField(required=False, min_value=0)
    magnetic = serializers.BooleanField(required=False)
    soluble = serializers.BooleanField(required=False)