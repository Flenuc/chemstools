from rest_framework import serializers
from .models import GlossaryTerm, PHCalculationHistory
from .validators import validate_ph_input, validate_buffer_input
from .utils import comprehensive_ph_calculation, calculate_buffer_capacity
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
        # Validar con cerberus
        if attrs['calculation_type'] == 'buffer_calculation':
            is_valid, normalized_data, warnings = validate_buffer_input(attrs)
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
            
            # Generar pasos si se solicita
            calculation_steps = None
            if validated_data.get('show_steps', False):
                calculation_steps = self._generate_calculation_steps(validated_data, results)
            
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