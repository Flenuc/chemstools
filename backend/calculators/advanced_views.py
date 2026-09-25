"""
Views avanzadas para calculadora de pH/pOH.
"""

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import HttpResponse
from django.db.models import Q, Avg, Count, Min, Max
from django.utils import timezone
from datetime import timedelta
import time
import logging
import uuid

from .models import PHCalculationHistory
from .serializers import (
    AdvancedPHCalculatorSerializer,
    PHCalculationHistorySerializer,
    BufferCalculationSerializer,
    ExportSerializer
)
from .export_utils import (
    export_to_csv,
    export_to_pdf,
    export_to_json,
    export_to_xlsx,
    create_download_url
)
from .utils import (
    comprehensive_ph_calculation,
    suggest_buffer_system,
    calculate_buffer_capacity
)

logger = logging.getLogger(__name__)


class AdvancedPHCalculatorView(APIView):
    """
    View avanzada para cálculos de pH/pOH con validación química robusta,
    cálculos extendidos y guardado en historial.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Realiza cálculo avanzado de pH/pOH con todas las funcionalidades.
        
        Acepta:
        - calculation_type: Tipo de cálculo
        - input_value: Valor de entrada
        - input_type: Tipo de valor (ph, poh, h_concentration, oh_concentration)
        - temperature: Temperatura en °C (opcional, default 25.0)
        - ionic_strength: Fuerza iónica en mol/L (opcional, default 0.0)
        - include_activity: Incluir corrección de actividad (opcional, default False)
        - show_steps: Mostrar pasos detallados (opcional, default False)
        - buffer_components: Lista de componentes buffer (opcional)
        
        Devuelve:
        - results: Resultados del cálculo (pH, pOH, concentraciones, etc.)
        - calculation_steps: Pasos detallados si se solicita
        - warnings: Advertencias químicas
        - metadata: Información del cálculo (ID, tiempo, metodología)
        """
        start_time = time.time()
        
        try:
            # Validación y serialización
            serializer = AdvancedPHCalculatorSerializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"Validation errors in pH calculation: {serializer.errors}")
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Realizar cálculo
            validated_data = serializer.validated_data
            calculation_result = serializer.calculate(validated_data)
            
            if not calculation_result['success']:
                logger.error(f"Calculation error: {calculation_result.get('error')}")
                return Response({
                    'success': False,
                    'error': calculation_result.get('error', 'Error en el cálculo')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Guardar en historial
            try:
                calculation_time_ms = calculation_result['metadata']['calculation_time_ms']
                
                history_entry = PHCalculationHistory.objects.create(
                    user=request.user,
                    calculation_type=validated_data['calculation_type'],
                    input_data=validated_data,
                    results=calculation_result['results'],
                    calculation_steps=calculation_result.get('calculation_steps'),
                    warnings=calculation_result.get('warnings', []),
                    temperature=validated_data.get('temperature', 25.0),
                    ionic_strength=validated_data.get('ionic_strength'),
                    calculation_time_ms=calculation_time_ms
                )
                
                calculation_result['metadata']['history_id'] = str(history_entry.id)
                logger.info(f"pH calculation saved to history: {history_entry.id}")
                
            except Exception as e:
                logger.error(f"Error saving to history: {e}")
                # No fallar si el guardado falla, pero log el error
            
            # Agregar sugerencias de buffer si es relevante
            if ('buffer_components' not in validated_data or 
                not validated_data.get('buffer_components')) and \
               calculation_result['results'].get('ph'):
                
                buffer_suggestion = suggest_buffer_system(calculation_result['results']['ph'])
                if buffer_suggestion:
                    calculation_result['buffer_suggestion'] = buffer_suggestion
            
            return Response(calculation_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Unexpected error in pH calculation: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PHCalculationHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para consultar y gestionar el historial de cálculos de pH del usuario.
    Permite operaciones de lectura y eliminación.
    """
    serializer_class = PHCalculationHistorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'delete', 'head', 'options']  # Solo permitir GET y DELETE
    
    def get_queryset(self):
        """Devuelve solo los cálculos del usuario autenticado."""
        queryset = PHCalculationHistory.objects.filter(user=self.request.user)
        
        # Filtros opcionales
        calculation_type = self.request.query_params.get('calculation_type')
        if calculation_type:
            queryset = queryset.filter(calculation_type=calculation_type)
        
        has_warnings = self.request.query_params.get('has_warnings')
        if has_warnings is not None:
            if has_warnings.lower() == 'true':
                queryset = queryset.exclude(warnings=[])
            else:
                queryset = queryset.filter(warnings=[])
        
        # Filtro por rango de fechas
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')
    
    def get_ordering(self):
        """Permite ordenación personalizada."""
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed_orderings = [
            'created_at', '-created_at',
            'calculation_time_ms', '-calculation_time_ms',
            'calculation_type', '-calculation_type'
        ]
        
        if ordering in allowed_orderings:
            return [ordering]
        return ['-created_at']
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un cálculo del historial.
        Solo permite eliminar cálculos propios del usuario.
        """
        instance = self.get_object()
        
        # Verificar que el cálculo pertenece al usuario
        if instance.user != request.user:
            return Response(
                {'error': 'No tienes permiso para eliminar este cálculo'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Log de la eliminación
        logger.info(f"Usuario {request.user.username} eliminó cálculo {instance.id}")
        
        # Eliminar el cálculo
        instance.delete()
        
        return Response(
            {'message': 'Cálculo eliminado exitosamente'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Proporciona un resumen estadístico del historial del usuario.
        """
        queryset = self.get_queryset()
        
        summary_data = {
            'total_calculations': queryset.count(),
            'calculation_types': {},
            'recent_activity': {},
            'performance_stats': {}
        }
        
        if summary_data['total_calculations'] > 0:
            # Estadísticas por tipo
            for calc_type, display_name in PHCalculationHistory.CALCULATION_TYPE_CHOICES:
                count = queryset.filter(calculation_type=calc_type).count()
                if count > 0:
                    summary_data['calculation_types'][calc_type] = {
                        'count': count,
                        'display_name': display_name,
                        'percentage': round((count / summary_data['total_calculations']) * 100, 1)
                    }
            
            # Actividad reciente (últimos 7 días)
            week_ago = timezone.now() - timedelta(days=7)
            recent_count = queryset.filter(created_at__gte=week_ago).count()
            summary_data['recent_activity'] = {
                'last_7_days': recent_count,
                'daily_average': round(recent_count / 7, 1)
            }
            
            # Estadísticas de rendimiento
            perf_stats = queryset.aggregate(
                avg_time=Avg('calculation_time_ms'),
                total_warnings=Count('id', filter=Q(warnings__isnull=False))
            )
            
            summary_data['performance_stats'] = {
                'average_calculation_time_ms': round(perf_stats['avg_time'] or 0, 2),
                'calculations_with_warnings': perf_stats['total_warnings'],
                'warning_rate_percentage': round(
                    (perf_stats['total_warnings'] / summary_data['total_calculations']) * 100, 1
                )
            }
        
        return Response(summary_data)


class ExportPHCalculationsView(APIView):
    """
    View para exportar cálculos de pH en diferentes formatos.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Genera export de cálculos en formato solicitado.
        
        Acepta:
        - calculation_ids: Lista de IDs a exportar
        - format: Formato (csv, pdf, json, xlsx)
        - include_steps: Incluir pasos detallados
        - include_warnings: Incluir warnings
        
        Devuelve:
        - download_url: URL temporal de descarga
        - expires_at: Fecha de expiración
        - file_size_bytes: Tamaño del archivo
        - total_calculations: Número de cálculos exportados
        """
        serializer = ExportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            # Obtener cálculos del usuario
            calculations = PHCalculationHistory.objects.filter(
                id__in=validated_data['calculation_ids'],
                user=request.user
            ).order_by('-created_at')
            
            if not calculations.exists():
                return Response({
                    'success': False,
                    'error': 'No se encontraron cálculos para exportar'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Generar export según formato
            export_format = validated_data['format']
            include_steps = validated_data.get('include_steps', False)
            include_warnings = validated_data.get('include_warnings', True)
            
            if export_format == 'csv':
                file_path, file_size = export_to_csv(calculations, include_steps, include_warnings)
            elif export_format == 'pdf':
                file_path, file_size = export_to_pdf(calculations, include_steps, include_warnings)
            elif export_format == 'json':
                file_path, file_size = export_to_json(calculations, include_steps, include_warnings)
            elif export_format == 'xlsx' or export_format == 'excel':
                file_path, file_size = export_to_xlsx(calculations, include_steps, include_warnings)
            else:
                return Response({
                    'success': False,
                    'error': f'Formato no soportado: {export_format}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear URL temporal de descarga
            download_url, expires_at = create_download_url(file_path, expires_in_hours=24)
            
            return Response({
                'success': True,
                'data': {
                    'download_url': download_url,
                    'expires_at': expires_at.isoformat(),
                    'file_size_bytes': file_size,
                    'total_calculations': calculations.count(),
                    'format': export_format,
                    'includes_steps': include_steps,
                    'includes_warnings': include_warnings
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error during export generation: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Error generando la exportación'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PHCalculationStatsView(APIView):
    """
    View para estadísticas de uso de la calculadora de pH del usuario.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Obtiene estadísticas detalladas de uso del usuario.
        
        Devuelve:
        - usage_stats: Estadísticas generales de uso
        - calculation_trends: Tendencias de cálculos por período
        - performance_metrics: Métricas de rendimiento
        - chemistry_insights: Insights químicos basados en los datos
        """
        try:
            user_calculations = PHCalculationHistory.objects.filter(user=request.user)
            
            if not user_calculations.exists():
                return Response({
                    'message': 'No hay cálculos registrados para este usuario',
                    'usage_stats': self._get_empty_stats()
                })
            
            stats = {
                'usage_stats': self._get_usage_stats(user_calculations),
                'calculation_trends': self._get_calculation_trends(user_calculations),
                'performance_metrics': self._get_performance_metrics(user_calculations),
                'chemistry_insights': self._get_chemistry_insights(user_calculations)
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating pH calculation stats: {e}", exc_info=True)
            return Response({
                'error': 'Error generando estadísticas'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_empty_stats(self):
        """Devuelve estructura de estadísticas vacía."""
        return {
            'total_calculations': 0,
            'calculation_types': {},
            'accuracy_rate': 0,
            'average_time_ms': 0,
            'favorite_calculation_type': None
        }

    def _get_usage_stats(self, calculations):
        """Calcula estadísticas generales de uso."""
        total = calculations.count()
        
        # Distribución por tipo de cálculo
        type_distribution = {}
        for calc_type, display_name in PHCalculationHistory.CALCULATION_TYPE_CHOICES:
            count = calculations.filter(calculation_type=calc_type).count()
            if count > 0:
                type_distribution[calc_type] = {
                    'count': count,
                    'percentage': round((count / total) * 100, 1),
                    'display_name': display_name
                }
        
        # Tipo favorito
        favorite_type = max(type_distribution.items(), 
                          key=lambda x: x[1]['count'])[0] if type_distribution else None
        
        return {
            'total_calculations': total,
            'calculation_types': type_distribution,
            'favorite_calculation_type': favorite_type,
            'calculations_with_warnings': calculations.exclude(warnings=[]).count(),
            'warning_rate': round((calculations.exclude(warnings=[]).count() / total) * 100, 1)
        }

    def _get_calculation_trends(self, calculations):
        """Analiza tendencias de cálculos por período."""
        now = timezone.now()
        
        # Últimos 30 días
        last_30_days = calculations.filter(
            created_at__gte=now - timedelta(days=30)
        ).count()
        
        # Últimos 7 días
        last_7_days = calculations.filter(
            created_at__gte=now - timedelta(days=7)
        ).count()
        
        # Último día
        last_24_hours = calculations.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        
        return {
            'last_24_hours': last_24_hours,
            'last_7_days': last_7_days,
            'last_30_days': last_30_days,
            'daily_average_last_week': round(last_7_days / 7, 1),
            'daily_average_last_month': round(last_30_days / 30, 1)
        }

    def _get_performance_metrics(self, calculations):
        """Calcula métricas de rendimiento."""
        # Estadísticas de tiempo
        time_stats = calculations.aggregate(
            avg_time=Avg('calculation_time_ms'),
            min_time=Min('calculation_time_ms'),
            max_time=Max('calculation_time_ms')
        )
        
        # Distribución de tiempos
        fast_calculations = calculations.filter(calculation_time_ms__lt=100).count()
        medium_calculations = calculations.filter(
            calculation_time_ms__gte=100, 
            calculation_time_ms__lt=500
        ).count()
        slow_calculations = calculations.filter(calculation_time_ms__gte=500).count()
        
        total = calculations.count()
        
        return {
            'average_time_ms': round(time_stats['avg_time'] or 0, 2),
            'fastest_calculation_ms': time_stats['min_time'],
            'slowest_calculation_ms': time_stats['max_time'],
            'speed_distribution': {
                'fast_calculations': {
                    'count': fast_calculations,
                    'percentage': round((fast_calculations / total) * 100, 1)
                },
                'medium_calculations': {
                    'count': medium_calculations,
                    'percentage': round((medium_calculations / total) * 100, 1)
                },
                'slow_calculations': {
                    'count': slow_calculations,
                    'percentage': round((slow_calculations / total) * 100, 1)
                }
            }
        }

    def _get_chemistry_insights(self, calculations):
        """Genera insights químicos basados en los datos del usuario."""
        insights = []
        
        # Análisis de pH favoritos
        ph_values = []
        for calc in calculations:
            if calc.results and 'ph' in calc.results:
                ph_values.append(calc.results['ph'])
        
        if ph_values:
            avg_ph = sum(ph_values) / len(ph_values)
            
            if avg_ph < 7:
                insights.append({
                    'type': 'ph_preference',
                    'message': f'Tiendes a trabajar con sistemas ácidos (pH promedio: {avg_ph:.1f})',
                    'recommendation': 'Considera explorar sistemas básicos para ampliar tu conocimiento'
                })
            elif avg_ph > 7:
                insights.append({
                    'type': 'ph_preference',
                    'message': f'Tiendes a trabajar con sistemas básicos (pH promedio: {avg_ph:.1f})',
                    'recommendation': 'Considera explorar sistemas ácidos para ampliar tu conocimiento'
                })
            else:
                insights.append({
                    'type': 'ph_preference',
                    'message': f'Trabajas con sistemas neutros (pH promedio: {avg_ph:.1f})',
                    'recommendation': 'Excelente balance entre sistemas ácidos y básicos'
                })
        
        # Análisis de uso de funcionalidades avanzadas
        advanced_calcs = calculations.filter(
            Q(calculation_type='buffer_calculation') |
            Q(calculation_type='activity_correction') |
            Q(ionic_strength__gt=0.1)
        ).count()
        
        if advanced_calcs > 0:
            advanced_percentage = (advanced_calcs / calculations.count()) * 100
            insights.append({
                'type': 'advanced_usage',
                'message': f'{advanced_percentage:.1f}% de tus cálculos usan funcionalidades avanzadas',
                'recommendation': 'Estás aprovechando bien las capacidades avanzadas de la herramienta'
            })
        else:
            insights.append({
                'type': 'advanced_usage',
                'message': 'No has utilizado funcionalidades avanzadas como buffers o corrección de actividad',
                'recommendation': 'Considera explorar cálculos más complejos para profundizar tu aprendizaje'
            })
        
        # Análisis de warnings
        calculations_with_warnings = calculations.exclude(warnings=[]).count()
        if calculations_with_warnings > 0:
            warning_rate = (calculations_with_warnings / calculations.count()) * 100
            if warning_rate > 30:
                insights.append({
                    'type': 'warning_pattern',
                    'message': f'{warning_rate:.1f}% de tus cálculos generan advertencias',
                    'recommendation': 'Revisa los rangos de entrada para evitar condiciones extremas'
                })
        
        return insights


class BufferCalculatorView(APIView):
    """
    View especializada para cálculos de sistemas buffer.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Realiza cálculos especializados de sistemas buffer.
        
        Acepta:
        - buffer_components: Lista de componentes del buffer
        - target_ph: pH objetivo (opcional)
        - temperature: Temperatura (opcional)
        - calculate_capacity: Calcular capacidad buffer (opcional)
        """
        serializer = BufferCalculationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        
        try:
            start_time = time.time()
            
            # Preparar datos para cálculo avanzado
            calc_data = {
                'calculation_type': 'buffer_calculation',
                'input_type': 'ph',
                'input_value': validated_data.get('target_ph', 7.0),
                'temperature': validated_data.get('temperature', 25.0),
                'buffer_components': validated_data['buffer_components'],
                'show_steps': True
            }
            
            # Usar el calculador avanzado
            results = comprehensive_ph_calculation(calc_data)
            
            # Cálculos específicos de buffer
            if validated_data.get('calculate_capacity', True):
                buffer_capacity = calculate_buffer_capacity(
                    results['ph'], 
                    validated_data['buffer_components']
                )
                results['buffer_capacity'] = buffer_capacity
            
            # Análisis del sistema buffer
            buffer_analysis = self._analyze_buffer_system(
                validated_data['buffer_components'], 
                results
            )
            
            calculation_time_ms = int((time.time() - start_time) * 1000)
            
            # Guardar en historial
            history_entry = PHCalculationHistory.objects.create(
                user=request.user,
                calculation_type='buffer_calculation',
                input_data=calc_data,
                results=results,
                warnings=buffer_analysis.get('warnings', []),
                temperature=validated_data.get('temperature', 25.0),
                calculation_time_ms=calculation_time_ms
            )
            
            return Response({
                'success': True,
                'results': results,
                'buffer_analysis': buffer_analysis,
                'metadata': {
                    'calculation_id': str(history_entry.id),
                    'calculation_time_ms': calculation_time_ms
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in buffer calculation: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Error en el cálculo de buffer'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _analyze_buffer_system(self, components, results):
        """Analiza las características del sistema buffer."""
        analysis = {
            'effectiveness': 'unknown',
            'recommendations': [],
            'warnings': []
        }
        
        total_concentration = sum(comp['concentration'] for comp in components)
        
        # Análisis de efectividad
        if total_concentration < 0.01:
            analysis['effectiveness'] = 'low'
            analysis['warnings'].append('Concentración total baja: capacidad buffer limitada')
        elif total_concentration > 0.1:
            analysis['effectiveness'] = 'high'
        else:
            analysis['effectiveness'] = 'medium'
        
        # Recomendaciones basadas en pH
        if 'ph' in results:
            ph = results['ph']
            for comp in components:
                if 'pka' in comp:
                    pka = comp['pka']
                    difference = abs(ph - pka)
                    if difference > 1.0:
                        analysis['recommendations'].append(
                            f'El pH ({ph:.1f}) está lejos del pKa ({pka:.1f}). '
                            f'Considera ajustar las concentraciones.'
                        )
        
        return analysis