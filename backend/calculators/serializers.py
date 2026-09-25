from rest_framework import serializers
from .models import GlossaryTerm, PHCalculationHistory, ChemicalPreset, BufferSystem
from .validators import validate_ph_input, validate_buffer_input
from .utils import comprehensive_ph_calculation, calculate_buffer_capacity
from .calculation_steps import (
    generate_concentration_to_ph_steps,
    generate_ph_to_all_steps,
    generate_buffer_steps,
    generate_activity_correction_steps
)
import time
import uuid


class GlossaryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryTerm
        fields = ['id', 'term', 'definition', 'created_at', 'updated_at']


class AdvancedPHCalculatorSerializer(serializers.Serializer):
    """
    Serializer avanzado para cálculos de pH/pOH con validación química robusta.
    """
    
    calculation_type = serializers.ChoiceField(
        choices=[
            ('ph_to_all', 'pH a todas las variables'),
            ('concentration_to_ph', 'Concentración a pH'),
            ('buffer_calculation', 'Cálculo de buffer'),
            ('ionic_strength', 'Cálculo de fuerza iónica'),
            ('activity_correction', 'Corrección de actividad'),
        ],
        help_text="Tipo de cálculo a realizar"
    )
    
    input_value = serializers.FloatField(
        min_value=0,
        help_text="Valor de entrada para el cálculo"
    )
    
    input_type = serializers.ChoiceField(
        choices=[
            ('ph', 'pH'),
            ('poh', 'pOH'),
            ('h_concentration', 'Concentración de H+'),
            ('oh_concentration', 'Concentración de OH-'),
        ],
        help_text="Tipo de valor de entrada"
    )
    
    temperature = serializers.FloatField(
        default=25.0,
        min_value=0,
        max_value=100,
        help_text="Temperatura en °C"
    )
    
    ionic_strength = serializers.FloatField(
        default=0.0,
        min_value=0,
        max_value=5.0,
        help_text="Fuerza iónica en mol/L"
    )
    
    include_activity = serializers.BooleanField(
        default=False,
        help_text="Incluir corrección de coeficientes de actividad"
    )
    
    show_steps = serializers.BooleanField(
        default=False,
        help_text="Mostrar pasos detallados del cálculo"
    )
    
    buffer_components = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        help_text="Componentes del sistema buffer"
    )

    def validate(self, attrs):
        """Validación completa usando cerberus."""
        # Para cálculos de buffer, necesitamos manejar la validación de forma especial
        if attrs['calculation_type'] == 'buffer_calculation':
            # Verificar que buffer_components esté presente
            if 'buffer_components' not in attrs or not attrs['buffer_components']:
                raise serializers.ValidationError({
                    'buffer_components': 'Se requieren componentes del buffer para este tipo de cálculo'
                })
            
            # Crear una copia de los datos para validación de buffer
            buffer_data = {
                'buffer_components': attrs['buffer_components'],
                'temperature': attrs.get('temperature', 25.0),
                'target_ph': attrs.get('input_value')  # Usar input_value como target_ph
            }
            
            is_valid, normalized_buffer_data, warnings = validate_buffer_input(buffer_data)
            
            if not is_valid:
                raise serializers.ValidationError("Datos del buffer inválidos")
            
            # Combinar los datos normalizados
            normalized_data = attrs.copy()
            normalized_data.update(normalized_buffer_data)
            normalized_data['calculation_type'] = attrs['calculation_type']
            normalized_data['input_type'] = attrs.get('input_type', 'ph')
            normalized_data['input_value'] = attrs.get('input_value', 7.0)
            
        else:
            is_valid, normalized_data, warnings = validate_ph_input(attrs)
            
            if not is_valid:
                raise serializers.ValidationError("Datos de entrada inválidos")
        
        # Guardar warnings para uso posterior
        self._warnings = warnings
        return normalized_data

    def calculate(self, validated_data):
        """
        Realiza el cálculo principal utilizando chemistry_utils.
        
        Args:
            validated_data: Datos validados
            
        Returns:
            dict: Resultados del cálculo con metadatos
        """
        start_time = time.time()
        
        try:
            # Realizar cálculo principal
            results = comprehensive_ph_calculation(validated_data)
            
            # Calcular tiempo de ejecución
            calculation_time_ms = int((time.time() - start_time) * 1000)
            
            # Generar pasos si se solicita (siempre generar para tener disponible)
            calculation_steps = self._generate_detailed_steps(validated_data, results)
            
            return {
                'success': True,
                'results': results,
                'calculation_steps': calculation_steps,
                'warnings': getattr(self, '_warnings', []),
                'metadata': {
                    'calculation_id': str(uuid.uuid4()),
                    'calculation_time_ms': calculation_time_ms,
                    'temperature': validated_data.get('temperature', 25.0),
                    'methodology': self._get_methodology_description(validated_data)
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'calculation_time_ms': int((time.time() - start_time) * 1000)
            }

    def _generate_calculation_steps(self, input_data, results):
        """Genera pasos detallados del cálculo."""
        steps = []
        
        input_type = input_data['input_type']
        input_value = input_data['input_value']
        temperature = input_data.get('temperature', 25.0)
        
        # Paso 1: Valor inicial
        if input_type == 'ph':
            steps.append(f"1. Valor inicial: pH = {input_value}")
            steps.append(f"2. Cálculo de [H+]: [H+] = 10^(-{input_value}) = {results['h_concentration']:.2e} M")
        elif input_type == 'h_concentration':
            steps.append(f"1. Valor inicial: [H+] = {input_value:.2e} M")
            steps.append(f"2. Cálculo de pH: pH = -log([H+]) = -log({input_value:.2e}) = {results['ph']:.2f}")
        
        # Paso 2: Kw corregido
        if temperature != 25.0:
            steps.append(f"3. Corrección de Kw para {temperature}°C: Kw = {results['corrected_kw']:.2e}")
        else:
            steps.append(f"3. Kw a 25°C: Kw = {results['corrected_kw']:.2e}")
        
        # Paso 3: Concentración de OH-
        steps.append(f"4. Cálculo de [OH-]: [OH-] = Kw/[H+] = {results['corrected_kw']:.2e}/{results['h_concentration']:.2e} = {results['oh_concentration']:.2e} M")
        
        # Paso 4: pOH
        steps.append(f"5. Cálculo de pOH: pOH = -log([OH-]) = -log({results['oh_concentration']:.2e}) = {results['poh']:.2f}")
        
        # Pasos adicionales para corrección de actividad
        if input_data.get('include_activity', False) and input_data.get('ionic_strength', 0) > 0:
            steps.append(f"6. Corrección por actividad: γ±(H+) = {results['activity_coefficient_h']:.3f} (Debye-Hückel)")
            steps.append(f"7. Actividad de H+: {results['h_concentration']:.2e} × {results['activity_coefficient_h']:.3f} = {results['h_concentration'] * results['activity_coefficient_h']:.2e}")
        
        # Pasos para buffer
        if 'buffer_capacity' in results:
            steps.append(f"8. Capacidad buffer: β = {results['buffer_capacity']:.4f} mol/L/pH")
        
        return steps
    
    def _generate_detailed_steps(self, input_data, results):
        """Genera pasos detallados del cálculo con fórmulas completas."""
        try:
            calculation_type = input_data.get('calculation_type')
            input_type = input_data.get('input_type')
            input_value = input_data.get('input_value')
            temperature = input_data.get('temperature', 25.0)
            
            # Usar las nuevas funciones de pasos detallados
            if calculation_type == 'concentration_to_ph':
                return generate_concentration_to_ph_steps(
                    input_type=input_type,
                    input_value=input_value,
                    temperature=temperature,
                    include_activity=input_data.get('include_activity', False),
                    ionic_strength=input_data.get('ionic_strength')
                )
            elif calculation_type == 'ph_to_all':
                # Convert 'ph' to 'pH' and 'poh' to 'pOH' (not all uppercase)
                if input_type == 'ph':
                    formatted_input_type = 'pH'
                elif input_type == 'poh':
                    formatted_input_type = 'pOH'
                else:
                    formatted_input_type = input_type
                    
                return generate_ph_to_all_steps(
                    input_type=formatted_input_type,
                    input_value=input_value,
                    temperature=temperature
                )
            elif calculation_type == 'buffer_calculation':
                return generate_buffer_steps(
                    target_ph=input_value,
                    buffer_components=input_data.get('buffer_components', []),
                    temperature=temperature
                )
            elif calculation_type == 'activity_correction':
                ph_initial = results.get('ph', 7.0)
                return generate_activity_correction_steps(
                    ph_initial=ph_initial,
                    ionic_strength=input_data.get('ionic_strength', 0),
                    temperature=temperature
                )
            else:
                # Fallback al método anterior si no hay tipo específico
                return self._generate_calculation_steps(input_data, results)
        except Exception as e:
            # En caso de error, usar el método anterior
            return self._generate_calculation_steps(input_data, results)

    def _get_methodology_description(self, input_data):
        """Describe la metodología utilizada."""
        methodology = "Ecuaciones fundamentales de equilibrio ácido-base"
        
        if input_data.get('include_activity', False):
            methodology += " con corrección de Debye-Hückel"
        
        if input_data.get('temperature', 25.0) != 25.0:
            methodology += " y corrección de temperatura"
        
        return methodology


class PHCalculationHistorySerializer(serializers.ModelSerializer):
    """
    Serializer para el historial de cálculos de pH.
    """
    
    calculation_type_display = serializers.CharField(
        source='get_calculation_type_display', 
        read_only=True
    )
    
    formatted_results = serializers.SerializerMethodField()
    has_warnings = serializers.BooleanField(read_only=True)
    calculation_duration_seconds = serializers.FloatField(read_only=True)
    
    class Meta:
        model = PHCalculationHistory
        fields = [
            'id', 'calculation_type', 'calculation_type_display',
            'input_data', 'results', 'formatted_results',
            'calculation_steps', 'warnings', 'has_warnings',
            'temperature', 'ionic_strength', 'calculation_time_ms',
            'calculation_duration_seconds', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'calculation_type_display',
            'formatted_results', 'has_warnings', 'calculation_duration_seconds'
        ]

    def get_formatted_results(self, obj):
        """Devuelve resultados formateados."""
        return obj.get_formatted_results()

    def to_representation(self, instance):
        """Personaliza la representación de salida."""
        data = super().to_representation(instance)
        
        # Agregar información del usuario si existe
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                'username': instance.user.username
            }
        else:
            data['user'] = None
        
        # Formatear fechas de manera más amigable
        if 'created_at' in data:
            data['created_at_formatted'] = instance.created_at.strftime('%d/%m/%Y %H:%M')
        
        return data


class BufferCalculationSerializer(serializers.Serializer):
    """
    Serializer específico para cálculos de buffer.
    """
    
    buffer_components = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        help_text="Lista de componentes del buffer"
    )
    
    target_ph = serializers.FloatField(
        required=False,
        min_value=0,
        max_value=14,
        help_text="pH objetivo del buffer"
    )
    
    temperature = serializers.FloatField(
        default=25.0,
        min_value=0,
        max_value=100,
        help_text="Temperatura en °C"
    )
    
    calculate_capacity = serializers.BooleanField(
        default=True,
        help_text="Calcular capacidad buffer"
    )

    def validate_buffer_components(self, value):
        """Valida los componentes del buffer."""
        for component in value:
            required_fields = ['compound', 'concentration']
            for field in required_fields:
                if field not in component:
                    raise serializers.ValidationError(f"Campo requerido '{field}' faltante en componente")
            
            if component['concentration'] <= 0:
                raise serializers.ValidationError("La concentración debe ser positiva")
            
            if component['concentration'] > 10:
                raise serializers.ValidationError("Concentración muy alta (>10M)")
        
        return value


class ExportSerializer(serializers.Serializer):
    """
    Serializer para exportación de cálculos.
    """
    
    calculation_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100,
        help_text="Lista de IDs de cálculos a exportar"
    )
    
    format = serializers.ChoiceField(
        choices=[
            ('csv', 'CSV'),
            ('pdf', 'PDF'),
            ('json', 'JSON'),
            ('xlsx', 'Excel')
        ],
        default='json',
        help_text="Formato de exportación"
    )
    
    date_range = serializers.DictField(
        required=False,
        help_text="Rango de fechas opcional"
    )
    
    include_steps = serializers.BooleanField(
        default=False,
        help_text="Incluir pasos detallados en la exportación"
    )
    
    include_warnings = serializers.BooleanField(
        default=True,
        help_text="Incluir warnings en la exportación"
    )

    def validate_date_range(self, value):
        """Valida el rango de fechas."""
        if value:
            required_fields = ['start_date', 'end_date']
            for field in required_fields:
                if field not in value:
                    raise serializers.ValidationError(f"Campo requerido '{field}' en date_range")
        
        return value

    def validate_calculation_ids(self, value):
        """Valida que los IDs de cálculo existan."""
        existing_ids = PHCalculationHistory.objects.filter(
            id__in=value
        ).values_list('id', flat=True)
        
        missing_ids = set(value) - set(existing_ids)
        if missing_ids:
            raise serializers.ValidationError(
                f"Cálculos no encontrados: {list(missing_ids)}"
            )
        
        return value
    
class ChemicalPresetSerializer(serializers.ModelSerializer):
    """
    Serializer para presets químicos.
    """
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    calculation_type_display = serializers.CharField(
        source='get_calculation_type_display',
        read_only=True
    )
    
    class Meta:
        model = ChemicalPreset
        fields = [
            'id', 'code', 'name', 'category', 'category_display',
            'description', 'chemical_formula', 'calculation_type',
            'calculation_type_display', 'calculation_values',
            'difficulty_level', 'tags', 'usage_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'usage_count']
    
    def to_representation(self, instance):
        """Personaliza la representación de salida."""
        data = super().to_representation(instance)
        
        # Agregar información de dificultad
        difficulty_map = {
            1: 'Básico',
            2: 'Intermedio',
            3: 'Avanzado'
        }
        data['difficulty_display'] = difficulty_map.get(
            instance.difficulty_level, 
            'Desconocido'
        )
        
        # Formatear los valores del cálculo para el frontend
        if instance.calculation_values:
            data['formatted_values'] = self._format_calculation_values(
                instance.calculation_type,
                instance.calculation_values
            )
        
        return data
    
    def _format_calculation_values(self, calc_type, values):
        """Formatea los valores según el tipo de cálculo."""
        formatted = {}
        
        if calc_type == 'concentration_to_ph':
            formatted['input_type'] = values.get('input_type', 'h_concentration')
            formatted['input_value'] = values.get('input_value', 0.1)
            formatted['compound'] = values.get('compound', '')
            
        elif calc_type == 'ph_to_all':
            formatted['input_type'] = values.get('input_type', 'ph')
            formatted['input_value'] = values.get('input_value', 7.0)
            
        elif calc_type == 'buffer_calculation':
            formatted['buffer_components'] = values.get('buffer_components', [])
            formatted['target_ph'] = values.get('target_ph', 7.0)
        
        # Agregar temperatura si está presente
        if 'temperature' in values:
            formatted['temperature'] = values['temperature']
        
        return formatted


class BufferSystemSerializer(serializers.ModelSerializer):
    """
    Serializer para sistemas buffer.
    """
    effective_range = serializers.SerializerMethodField()
    is_suitable_for_neutral = serializers.SerializerMethodField()
    
    class Meta:
        model = BufferSystem
        fields = [
            'id', 'code', 'name', 'acid_formula', 'base_formula',
            'pka', 'effective_ph_min', 'effective_ph_max', 'optimal_ph',
            'effective_range', 'common_uses', 'preparation_notes',
            'is_suitable_for_neutral', 'usage_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'usage_count']
    
    def get_effective_range(self, obj):
        """Devuelve el rango efectivo como lista."""
        return [obj.effective_ph_min, obj.effective_ph_max]
    
    def get_is_suitable_for_neutral(self, obj):
        """Indica si es adecuado para pH neutro (7.0)."""
        return obj.is_suitable_for_ph(7.0)
    
    def to_representation(self, instance):
        """Personaliza la representación de salida."""
        data = super().to_representation(instance)
        
        # Agregar componentes formateados para el frontend
        data['components'] = {
            'acid': {
                'formula': instance.acid_formula,
                'pka': instance.pka
            },
            'base': {
                'formula': instance.base_formula
            }
        }
        
        # Calcular el rango de trabajo óptimo (pKa ± 1)
        data['optimal_range'] = [
            max(0, instance.pka - 1),
            min(14, instance.pka + 1)
        ]
        
        return data


class BufferSuggestionSerializer(serializers.Serializer):
    """
    Serializer para sugerencias de sistemas buffer.
    """
    buffer_system = BufferSystemSerializer(read_only=True)
    suitability_score = serializers.FloatField(read_only=True)
    distance_from_pka = serializers.FloatField(read_only=True)
    
    def to_representation(self, instance):
        """Personaliza la representación de salida."""
        data = super().to_representation(instance)
        
        # Agregar recomendación basada en el score
        score = instance['suitability_score']
        if score >= 0.9:
            data['recommendation'] = 'Excelente'
            data['recommendation_color'] = 'success'
        elif score >= 0.7:
            data['recommendation'] = 'Muy bueno'
            data['recommendation_color'] = 'success'
        elif score >= 0.5:
            data['recommendation'] = 'Bueno'
            data['recommendation_color'] = 'warning'
        else:
            data['recommendation'] = 'Aceptable'
            data['recommendation_color'] = 'info'
        
        # Formatear el score como porcentaje
        data['suitability_percentage'] = round(score * 100, 1)
        
        return data


class PresetUsageSerializer(serializers.Serializer):
    """
    Serializer para el uso de un preset.
    """
    preset_id = serializers.IntegerField(required=True)
    applied_at = serializers.DateTimeField(read_only=True)
    calculation_result_id = serializers.UUIDField(
        read_only=True,
        allow_null=True
    )


class BufferDesignRequestSerializer(serializers.Serializer):
    """
    Serializer para solicitud de diseño de buffer.
    """
    target_ph = serializers.FloatField(
        min_value=0,
        max_value=14,
        help_text="pH objetivo del buffer"
    )
    buffer_system_id = serializers.IntegerField(
        required=False,
        help_text="ID del sistema buffer a usar (opcional)"
    )
    total_concentration = serializers.FloatField(
        min_value=0.001,
        max_value=5.0,
        default=0.1,
        help_text="Concentración total del buffer (M)"
    )
    volume = serializers.FloatField(
        min_value=0.001,
        max_value=10.0,
        default=1.0,
        help_text="Volumen de la solución (L)"
    )
    temperature = serializers.FloatField(
        min_value=0,
        max_value=100,
        default=25.0,
        help_text="Temperatura (°C)"
    )
    
    def validate(self, attrs):
        """Validación personalizada."""
        # Si se especifica un sistema buffer, verificar que existe
        if 'buffer_system_id' in attrs:
            try:
                buffer_system = BufferSystem.objects.get(
                    id=attrs['buffer_system_id'],
                    is_active=True
                )
                # Verificar que el pH objetivo está en el rango del buffer
                if not buffer_system.is_suitable_for_ph(attrs['target_ph']):
                    raise serializers.ValidationError(
                        f"El pH objetivo {attrs['target_ph']} está fuera del "
                        f"rango efectivo del buffer {buffer_system.name} "
                        f"({buffer_system.effective_ph_min} - {buffer_system.effective_ph_max})"
                    )
                attrs['buffer_system'] = buffer_system
            except BufferSystem.DoesNotExist:
                raise serializers.ValidationError(
                    "Sistema buffer no encontrado o inactivo"
                )
        
        return attrs